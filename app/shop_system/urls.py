# The Unresolved reference 'shop_system' error seems to be incorrect
from shop_system.api import views
from django.urls import path

urlpatterns = [
    path("orders/<int:order_id>/split_shipment/", views.split_shipment, name="split-shipment")
]
