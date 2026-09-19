from django.db import models


class Device(models.Model):
    """Физическое устройство ESP32"""

    name = models.CharField(max_length=100, verbose_name="Название")
    device_id = models.IntegerField(
        unique=True,
        verbose_name="ID устройства",
        help_text="ID, который отправляет ESP32 (уникальный для каждой платы)"
    )
    plant = models.OneToOneField(
        'plants.Plant',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='device',
        verbose_name="Привязанное растение"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    last_seen = models.DateTimeField(null=True, blank=True, verbose_name="Последний сигнал")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"

    def __str__(self):
        return f"{self.name} (ID={self.device_id})"