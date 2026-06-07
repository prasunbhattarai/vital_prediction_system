from rest_framework import serializers
from .models import AnomalyResult


class PredictOutputSerializer(serializers.Serializer):
    status = serializers.CharField()
    cpu_usage = serializers.FloatField(required=False)
    memory_usage = serializers.FloatField(required=False)
    anomaly = serializers.IntegerField(required=False)
    time = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    length = serializers.IntegerField(required=False)


class AnomalyResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnomalyResult
        fields = '__all__'
