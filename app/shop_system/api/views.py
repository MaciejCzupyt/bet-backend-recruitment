import datetime
import logging

from django.utils import timezone
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
# The Unresolved reference 'shop_system' error seems to be incorrect
from shop_system.api.serializers import SplitShipmentSerializer
from ..models import Order, Logistic, OperationLog


@api_view(["POST"])
def split_shipment(request, order_id):
    # validate request, throw 400 for bad data
    serializer = SplitShipmentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"message": "Incorrect data format"}, status=400)

    product_ids = serializer.validated_data["product_ids"]
    address = serializer.validated_data["address"]

    # verify if order exists or 404
    order = get_object_or_404(Order, id=order_id)

    # flag for future use in case a request is made to move the products to the same address as the original order
    same_address = (address == order.address)

    """
    TODO this fragment might be detrimental
    A user could request a ship_splitment for a product and then change his mind and request it to be delivered to the
    original address again
    """
    # if order.address == address:
    #     return Response({"message": "New address cannot be the same as the source address"}, status=400)

    """
    To figure out exactly where each product could've come from due to the potential of multiple logistics objects
    existing, a new variable is created that tracks each address. If it turns out that all the products originated from
    additionally created logistic objects and none from the original order object, then the source addresses shouldn't
    mention the original source address.
    """
    source_addresses = [order.address]
    address_counter = len(product_ids)

    # verify if products exist in given order or 404
    if not order.products.filter(id__in=product_ids).count() == len(product_ids):
        return Response({"message": "Order does not contain the specified products"}, status=404)

    # check if attempting to move products that are already set to move to specified address
    related_logistic = Logistic.objects.filter(order=order, address=address).first()
    if related_logistic:
        if set(product_ids) & set(related_logistic.serialized_products):
            return Response({
                "message": "Some of the products are already headed towards the specified address"
            }, status=400)

    # remove given product_ids from existing logistic objects tied to this order
    related_logistics = Logistic.objects.filter(order=order)
    if related_logistics is None and same_address:
        return Response({"message": "The products belong to the same address as the original order"}, status=400)
    for logistic in related_logistics:
        old_products = logistic.serialized_products
        new_products = [product_id for product_id in old_products if product_id not in product_ids]
        if old_products != new_products:
            # add logistic address as a source address
            source_addresses.append(logistic.address)
            address_counter = address_counter - (len(old_products) - len(new_products))
            if new_products:
                logistic.serialized_products = new_products
                logistic.save()
            else:
                # delete logistic with no products
                logistic.delete()

    # remove original order address if all products came from different logistic objects
    if address_counter == 0:
        source_addresses.remove(order.address)
    elif same_address:
        return Response({"message": "Some of the products belong to the same address as the original order"}, status=400)

    # check for logistic with existing address, create new one if none exist
    if not same_address:
        logistic_with_address, created = Logistic.objects.get_or_create(
            order=order,
            address=address,
            defaults={"serialized_products": list(product_ids)}
        )

        if not created:
            new_list = list(logistic_with_address.serialized_products)
            new_list.extend(product_ids)
            logistic_with_address.serialized_products = new_list
            logistic_with_address.save()

    # create new log object
    OperationLog.objects.create(
        operation="SHIPMENT_SPLIT",
        details={
            "user": getattr(request.user, "username", None) or "AnonymousUser",
            "timestamp": timezone.now().isoformat(),
            "product_ids": product_ids,
            "source_addresses": source_addresses,
            "target_address": address
        },
        order=order,
    )

    # throw 200
    return Response({"message": f"Shipment split successful to {address} for products: {product_ids}"})
