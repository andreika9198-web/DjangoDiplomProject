from django.conf import settings
from django.core.mail import send_mail


def send_register_email(email):
    """Приветственное письмо"""
    send_mail(
        subject='Добро пожаловать в Умный полив',
        message='Вы успешно зарегистрировались в системе Умный полив!',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )


def send_new_password_email(email, new_password):
    """Новый пароль"""
    send_mail(
        subject='Сброс пароля',
        message=f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )


def send_code_email(email, user_code):
    """Код подтверждения"""
    send_mail(
        subject='Сброс пароля',
        message=f'Код для сброса пароля: {user_code}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )