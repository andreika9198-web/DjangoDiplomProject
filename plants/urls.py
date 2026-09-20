from django.urls import path
from plants.views import (SensorDataAPIView, index, DeviceStateAPIView, control, video_feed,
                          CameraStateAPIView, video_feed, WateringLogAPIView, PlantListView,
                          device_state_page, plant_add, PlantUpdateView,  plant_delete)

app_name = 'plants'

urlpatterns = [
    path('', index, name='index'),
    path('control/', control, name='control'),
    path('api/sensor-data/', SensorDataAPIView.as_view(), name='sensor_data_api'),
    path('api/state/', DeviceStateAPIView.as_view(), name='device_state'),
    path('video_feed/', video_feed, name='video_feed'),
    path('api/camera/', CameraStateAPIView.as_view(), name='camera_state'),
    path('video_feed/', video_feed, name='video_feed'),
    path('api/watering-log/', WateringLogAPIView.as_view(), name='watering_log_api'),
    path('plants/', PlantListView.as_view(), name='plants_list'),
    path('control/state/', device_state_page, name='device_state_page'),
    path('plants/add/', plant_add, name='plant_add'),
    path('plants/<int:plant_id>/edit/', PlantUpdateView.as_view(), name='plant_id'),
    path('plants/<int:plant_id>/delete/', plant_delete, name='plant_delete'),
]