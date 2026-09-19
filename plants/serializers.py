from rest_framework import serializers
from .models import SensorData, Plant, CameraState,WateringLog

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


class CameraStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraState
        fields = ['is_on', 'updated_at']
        read_only_fields = ['updated_at']


class WateringLogSerializer(serializers.ModelSerializer):
    """Сериализатор для логов полива"""

    class Meta:
        model = WateringLog
        fields = ['plant', 'duration', 'source', 'success', 'comment']
        read_only_fields = ['started_at']