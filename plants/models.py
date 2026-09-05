from django.db import models

from django.db import models
from django.contrib.auth.models import User

NULLABLE = {'blank': True, 'null': True}

class Plant(models.Model):
    """Модель растения"""
    name = models.CharField(max_length=100, verbose_name="Название")
    min_humidity = models.IntegerField(default=30, verbose_name="Нижний порог влажности %")
    max_humidity = models.IntegerField(default=70, verbose_name="Верхний порог влажности %")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants', verbose_name="Владелец")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Растение"
        verbose_name_plural = "Растения"

class SensorData(models.Model):
    """Модель для хранения показаний датчиков"""
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data')
    humidity = models.FloatField(verbose_name="Влажность почвы %")
    temperature = models.FloatField(verbose_name="Температура °C", **NULLABLE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plant.name} - {self.humidity}% ({self.created_at.strftime('%H:%M')})"

    class Meta:
        verbose_name = "Показание датчика"
        verbose_name_plural = "Показания датчиков"
        ordering = ['-created_at']

class WateringLog(models.Model):
    """Модель для истории поливов"""
    SOURCES = [
        ('auto', 'Автоматический'),
        ('manual', 'Ручной (сайт)'),
        ('vk', 'Ручной (VK бот)'),
    ]
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='watering_logs')
    started_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=5, verbose_name="Длительность (секунд)")
    source = models.CharField(max_length=20, choices=SOURCES, default='auto', verbose_name="Источник")
    success = models.BooleanField(default=True, verbose_name="Успешно")
    comment = models.CharField(max_length=255, verbose_name="Комментарий", **NULLABLE)

    def __str__(self):
        return f"Полив {self.plant.name} - {self.source} ({self.started_at.strftime('%H:%M')})"

    class Meta:
        verbose_name = "Лог полива"
        verbose_name_plural = "Логи поливов"
        ordering = ['-started_at']