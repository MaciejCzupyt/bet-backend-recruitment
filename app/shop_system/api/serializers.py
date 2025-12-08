from rest_framework import serializers


class SplitShipmentSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)
    address = serializers.CharField(max_length=200)  # potentially change?
