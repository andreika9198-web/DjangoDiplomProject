from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Max, Min
from django.db.models.functions import TruncDate
from plants.models import Plant, SensorData, WateringLog
import json
from django.http import JsonResponse


def analytics_index(request):
    """Главная страница аналитики — список растений"""
    plants = Plant.objects.filter(is_active=True)
    return render(request, 'analytics/index.html', {
        'title': 'Аналитика',
        'plants': plants,
    })


def plant_chart(request, plant_id):
    """Страница с графиками для растения"""
    plant = get_object_or_404(Plant, id=plant_id)

    # Последние 100 записей датчиков
    data = SensorData.objects.filter(plant=plant).order_by('created_at')[:100]

    # Данные для графиков
    labels = [d.created_at.strftime('%d.%m %H:%M') for d in data]
    humidity = [d.humidity for d in data]
    temperature = [d.temperature if d.temperature else 0 for d in data]

    # Статистика
    stats = SensorData.objects.filter(plant=plant).aggregate(
        avg_h=Avg('humidity'),
        max_h=Max('humidity'),
        min_h=Min('humidity'),
        avg_t=Avg('temperature'),
        max_t=Max('temperature'),
        min_t=Min('temperature'),
    )

    # Логи полива
    logs = WateringLog.objects.filter(plant=plant).order_by('-started_at')[:20]

    # Поливы по дням
    watering_by_day = (WateringLog.objects
                       .filter(plant=plant)
                       .annotate(day=TruncDate('started_at'))
                       .values('day')
                       .annotate(count=Count('id'))
                       .order_by('day'))

    watering_dates = [w['day'].strftime('%d.%m') for w in watering_by_day]
    watering_counts = [w['count'] for w in watering_by_day]

    return render(request, 'analytics/plant_chart.html', {
        'title': f'Аналитика: {plant.name}',
        'plant': plant,
        'labels': json.dumps(labels),
        'humidity': json.dumps(humidity),
        'temperature': json.dumps(temperature),
        'stats': stats,
        'logs': logs,
        'watering_dates': json.dumps(watering_dates),
        'watering_counts': json.dumps(watering_counts),
    })


def sensors_page(request):
    """Страница с текущими показаниями датчиков"""
    from plants.models import Plant, SensorData

    plants = Plant.objects.filter(is_active=True)

    plants_data = []
    for plant in plants:
        latest = SensorData.objects.filter(plant=plant).order_by('-created_at').first()
        plants_data.append({
            'plant': plant,
            'latest': latest,
        })

    return render(request, 'analytics/sensors.html', {
        'title': 'Показания датчиков',
        'plants_data': plants_data,
    })


def sensors_api(request):
    """API для текущих показаний датчиков (JSON)"""
    plants = Plant.objects.filter(is_active=True)

    data = []
    for plant in plants:
        latest = SensorData.objects.filter(plant=plant).order_by('-created_at').first()
        if latest:
            data.append({
                'plant_id': plant.id,
                'plant_name': plant.name,
                'humidity': latest.humidity,
                'temperature': latest.temperature,
                'created_at': latest.created_at.strftime('%H:%M:%S'),
            })

    return JsonResponse({'plants': data})