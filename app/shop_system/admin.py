from django.contrib import admin
from .models import Product, Order, Logistic, OperationLog

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Logistic)
admin.site.register(OperationLog)