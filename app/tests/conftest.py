import pytest
from rest_framework.test import APIClient

from shop_system.models import Product, Order


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def order_with_products(db):
    product_1 = Product.objects.create(name="product_1", description="product_1", price=10)
    product_2 = Product.objects.create(name="product_2", description="product_2", price=20)
    order = Order.objects.create(address="address_1")
    order.products.set([product_1, product_2])

    return order, product_1, product_2


@pytest.fixture
def another_order_with_products(db):
    product_3 = Product.objects.create(name="product_3", description="product_3", price=30)
    product_4 = Product.objects.create(name="product_4", description="product_4", price=40)
    order = Order.objects.create(address="address_2")
    order.products.set([product_3, product_4])

    return order, product_3, product_4