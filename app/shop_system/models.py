from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=16)


class Order(models.Model):
    address = models.CharField(max_length=255)
    placed_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product, related_name="orders")
    """
    TODO if the delivery_date is properly implemented for the logistic model, then Order should likely have a
    delivery_date field as well along with all the logic associated with it in the view
    """


class Logistic(models.Model):
    order = models.ForeignKey(Order, related_name="logistics", on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    """
    TODO if the delivery_date is properly implemented for the logistic model, then Order should likely have a
    delivery_date field as well along with all the logic associated with it in the view
    """
    delivery_date = models.DateTimeField(null=True, blank=True)
    serialized_products = models.JSONField(default=list)

    # TODO without the implementation of delivery date, these 2 fields are always unique together
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "address"],
                name="unique_logistic_order_address"
            )
        ]


class OperationLog(models.Model):
    OPERATION_CHOICES = {
        "SHIPMENT_SPLIT": "SHIPMENT_SPLIT"
    }

    operation = models.CharField(choices=OPERATION_CHOICES)
    details = models.JSONField()
    order = models.ForeignKey(Order, related_name="operation_logs", on_delete=models.DO_NOTHING)

