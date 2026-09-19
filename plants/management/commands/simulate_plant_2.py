from django.core.management.base import BaseCommand
from plants.models import Plant, SensorData
import random


class Command(BaseCommand):
    help = 'Симулирует данные для растения №2 на основе растения №1'

    def handle(self, *args, **options):
        try:
            plant1 = Plant.objects.get(id=1)
            plant2 = Plant.objects.get(id=2)
        except Plant.DoesNotExist:
            self.stdout.write(self.style.ERROR('Растения с ID 1 или 2 не найдены'))
            return

        # Последние данные растения 1
        latest = SensorData.objects.filter(plant=plant1).order_by('-created_at').first()

        if not latest:
            self.stdout.write(self.style.ERROR('Нет данных для растения 1'))
            return

        # Создаём данные для растения 2 с небольшим отклонением
        humidity = max(0, min(100, latest.humidity + random.uniform(-5, 5)))
        temperature = (latest.temperature or 0) + random.uniform(-1, 1)

        SensorData.objects.create(
            plant=plant2,
            humidity=round(humidity, 1),
            temperature=round(temperature, 1),
        )

        self.stdout.write(self.style.SUCCESS(
            f'Созданы данные для {plant2.name}: '
            f'{round(humidity, 1)}%, {round(temperature, 1)}°C'
        ))