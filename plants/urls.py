from django.urls import path
from plants.views import SensorDataAPIView, index, DeviceStateAPIView

app_name = 'plants'

urlpatterns = [
    path('', index, name='index'),
    path('api/sensor-data/', SensorDataAPIView.as_view(), name='sensor_data_api'),
    path('api/state/', DeviceStateAPIView.as_view(), name='device_state'),
]