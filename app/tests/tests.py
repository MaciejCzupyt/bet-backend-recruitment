from django.urls import reverse
# incorrect Unresolved reference errors
from shop_system.models import Logistic, OperationLog
from django.contrib.auth.models import User


def test_split_shipment_creates_new_logistic_and_operationlog(client, order_with_products):
    order, product_1, product_2 = order_with_products
    new_address = "New Address"

    payload = {
        "product_ids": [product_2.id],
        "address": new_address
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    logistic = Logistic.objects.get(order=order, address=new_address)
    assert logistic.serialized_products == [product_2.id]

    operationlog = OperationLog.objects.get(order=order)
    assert operationlog.details["user"] == "test"
    assert operationlog.details["product_ids"] == [product_2.id]
    assert operationlog.details["source_addresses"] == [order.address]
    assert operationlog.details["target_address"] == new_address


def test_split_shipment_assigns_correct_user(client, order_with_products):
    order, product_1, product_2 = order_with_products

    user = User.objects.create(username="correct_user", password="test")
    client.force_authenticate(user=user)

    new_address = "New Address"
    payload = {
        "product_ids": [product_2.id],
        "address": new_address
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    operationlog = OperationLog.objects.get(order=order)
    assert operationlog.details["user"] == "correct_user"


def test_incorrect_request_returns_400(client, order_with_products):
    order, _, _ = order_with_products
    payload = {
        "A": [1, 2],
        "B": "foobar"
    }
    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 400


def test_missing_product_ids_returns_400(client, order_with_products):
    order, _, _ = order_with_products

    new_address = "New Address"
    payload = {
        "product_ids": [],
        "address": new_address
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 400


def test_missing_address_returns_400(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_2.id],
        "address": ""
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 400


def test_non_existing_order_returns_404(client, order_with_products, another_order_with_products):
    order_1, product_1, product_2 = order_with_products
    order_2, product_3, product_4 = another_order_with_products

    payload = {
        "product_ids": [product_2.id],
        "address": "new address"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order_2.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 404


def test_products_not_belonging_to_order_returns_404(client, order_with_products, another_order_with_products):
    order_1, product_1, product_2 = order_with_products
    order_2, product_3, product_4 = another_order_with_products

    payload = {
        "product_ids": [product_3.id],
        "address": "new address"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order_1.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 404


def test_source_addresses_with_multiple_logistics(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_1.id],
        "address": "new_address_1"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    payload = {
        "product_ids": [product_2.id],
        "address": "new_address_2"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    payload = {
        "product_ids": [product_1.id, product_2.id],
        "address": "new_address_3"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    logistics = Logistic.objects.all()
    assert len(logistics) == 1

    operationlog = OperationLog.objects.filter(order=order).last()
    assert operationlog.details["target_address"] == "new_address_3"
    assert operationlog.details["source_addresses"] == ["new_address_1", "new_address_2"]


def test_products_moved_to_existing_logistic_with_same_address(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_1.id],
        "address": "A"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    payload = {
        "product_ids": [product_2.id],
        "address": "A"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    logistic = Logistic.objects.get(order=order)
    assert logistic.serialized_products == [product_1.id, product_2.id]


def test_move_product_to_logistic_with_that_product(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_1.id],
        "address": "A"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    payload = {
        "product_ids": [product_1.id],
        "address": "A"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 400


def test_new_logistic_with_same_address_as_order_throws_400(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_1.id],
        "address": "address_1"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 400


def test_new_logistic_with_same_address_as_order_but_existing_logistic_deletes_product_from_logistic(client, order_with_products):
    order, product_1, product_2 = order_with_products

    payload = {
        "product_ids": [product_1.id],
        "address": "A"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200
    assert len(Logistic.objects.all()) == 1

    payload = {
        "product_ids": [product_1.id],
        "address": "address_1"
    }

    url = reverse("shop_system:split-shipment", kwargs={"order_id": order.id})
    response = client.post(url, payload, format="json")

    assert response.status_code == 200

    assert len(Logistic.objects.all()) == 0

