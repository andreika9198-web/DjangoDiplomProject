from rest_framework import serializers
from .models import SensorData, Plant

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['plant', 'humidity', 'temperature', 'created_at']
        read_only_fields = ['created_at']

    def validate_plant(self, value):
        """Проверка, что растение существует и активно"""
        if not value.is_active:
            raise serializers.ValidationError("Растение неактивно")
        return value