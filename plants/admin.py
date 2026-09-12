from django.contrib import admin
from .models import Plant, SensorData, WateringLog, DeviceState

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
    list_display = ('plant', 'source', 'duration', 'success', 'started_at')
    list_filter = ('source', 'success', 'plant')

@admin.register(DeviceState)
class DeviceStateAdmin(admin.ModelAdmin):
    list_display = ('automatic', 'pump', 'light', 'updated_at')
    list_filter = ('automatic', 'pump', 'light')