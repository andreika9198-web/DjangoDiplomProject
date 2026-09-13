from django.urls import path
from plants.views import (SensorDataAPIView, index, DeviceStateAPIView, control, video_feed,
                          CameraStateAPIView, video_feed)

app_name = 'plants'

urlpatterns = [
    path('', index, name='index'),
    path('control/', control, name='control'),
    path('api/sensor-data/', SensorDataAPIView.as_view(), name='sensor_data_api'),
    path('api/state/', DeviceStateAPIView.as_view(), name='device_state'),
    path('video_feed/', video_feed, name='video_feed'),
    path('api/camera/', CameraStateAPIView.as_view(), name='camera_state'),
    path('video_feed/', video_feed, name='video_feed'),
]