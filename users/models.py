from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

NULLABLE = {'blank': True, 'null': True}


class UserRoles(models.TextChoices):
    """Роли пользователей"""
    ADMIN = 'admin', _('admin')
    MODERATOR = 'moderator', _('moderator')
    USER = 'user', _('user')


def user_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return f'users/{instance.id}/avatar_{uuid.uuid4().hex}.{ext}'


class User(AbstractUser):
    """Кастомная модель пользователя (email вместо username)"""
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')
    role = models.CharField(
        max_length=9, choices=UserRoles.choices, default=UserRoles.USER)
    first_name = models.CharField(
        max_length=150, verbose_name='Имя', default='Anonymous')
    last_name = models.CharField(
        max_length=150, verbose_name='Фамилия', default='Anonymous')
    avatar = models.ImageField(
        upload_to=user_avatar_path, verbose_name='Аватар', **NULLABLE)
    phone = models.CharField(
        max_length=35, verbose_name='Телефон', **NULLABLE)

    # ← Заменяем telegram и max_messenger на vk_id
    vk_id = models.CharField(
        max_length=50, verbose_name='VK ID', **NULLABLE,
        help_text='ID пользователя ВКонтакте для уведомлений')

    is_active = models.BooleanField(default=True, verbose_name='Активен')
    verification_code = models.CharField(max_length=6, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f'{self.email} ({self.first_name} {self.last_name})'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']


from django.db import models

# Create your models here.
