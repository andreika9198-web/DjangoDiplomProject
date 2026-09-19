from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_index, name='index'),
    path('plant/<int:plant_id>/', views.plant_chart, name='plant_chart'),
    path('sensors/', views.sensors_page, name='sensors'),
    path('api/sensors/', views.sensors_api, name='sensors_api'),
]