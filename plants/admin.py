from django.contrib import admin
from .models import Plant, SensorData, WateringLog, DeviceState, CameraState

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_humidity', 'max_humidity', 'is_active', 'owner')
    list_filter = ('is_active', 'owner')
    search_fields = ('name',)

@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ('plant', 'humidity', 'temperature', 'created_at')
    list_filter = ('plant', 'created_at')

@admin.register(WateringLog)
class WateringLogAdmin(admin.ModelAdmin):
    list_display = (
        'plant', 'source', 'duration',
        'start_watering_time', 'end_watering_time',
        'success', 'started_at'
    )
    list_filter = ('source', 'success', 'plant')
    search_fields = ('plant__name',)

@admin.register(DeviceState)
class DeviceStateAdmin(admin.ModelAdmin):
    list_display = ('automatic', 'pump', 'light', 'updated_at')
    list_filter = ('automatic', 'pump', 'light')

@admin.register(CameraState)
class CameraStateAdmin(admin.ModelAdmin):
    list_display = ('is_on', 'updated_at')