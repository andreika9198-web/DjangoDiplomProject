from django.urls import path
from plants.views import SensorDataAPIView, index

app_name = 'plants'

urlpatterns = [
    path('', index, name='index'),
    path('api/sensor-data/', SensorDataAPIView.as_view(), name='sensor_data_api'),
]