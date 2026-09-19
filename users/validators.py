from django.core.exceptions import ValidationError
import re


def validate_password(password):
    """Валидация пароля: минимум 8 символов, буквы и цифры"""
    if len(password) < 8:
        raise ValidationError('Пароль должен содержать минимум 8 символов')

    if not re.search(r'[A-Za-z]', password):
        raise ValidationError('Пароль должен содержать хотя бы одну букву')

    if not re.search(r'\d', password):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру')