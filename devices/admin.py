from django.contrib import admin
from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'device_id', 'plant', 'is_active', 'last_seen')
    list_filter = ('is_active',)
    search_fields = ('name',)
    list_editable = ('plant', 'is_active')