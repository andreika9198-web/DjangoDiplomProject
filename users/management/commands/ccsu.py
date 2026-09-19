from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Создаёт тестовых пользователей (admin, moderator, user)'

    def handle(self, *args, **options):
        users = {
            'admin': {
                'email': 'admin@web.top',
                'role': 'admin',
                'first_name': 'Admin',
                'last_name': 'Adminov',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            },
            'moderator': {
                'email': 'moderator@web.top',
                'role': 'moderator',
                'first_name': 'Moder',
                'last_name': 'Moderov',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True
            },
            'user': {
                'email': 'user0@web.top',
                'role': 'user',
                'first_name': 'User',
                'last_name': 'Userov',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True
            },
        }

        for user, user_params in users.items():
            # Проверяем, нет ли уже такого пользователя
            if User.objects.filter(email=user_params['email']).exists():
                self.stdout.write(self.style.WARNING(
                    f'Пользователь {user} уже существует'
                ))
                continue

            # Создаём пользователя
            cr_user = User.objects.create(
                email=user_params['email'],
                role=user_params['role'],   # ← ДОБАВЛЕНО (было пропущено)
                first_name=user_params['first_name'],
                last_name=user_params['last_name'],
                is_staff=user_params['is_staff'],
                is_superuser=user_params['is_superuser'],
                is_active=user_params['is_active']
            )
            cr_user.set_password('qwerty')
            cr_user.save()

            self.stdout.write(self.style.SUCCESS(
                f'✅ Создан: {user} ({user_params["email"]}) — роль: {user_params["role"]}'
            ))