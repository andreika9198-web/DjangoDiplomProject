import random
import string

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView)
from django.views.generic import (
    CreateView, UpdateView, DetailView, ListView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from users.forms import (
    UserRegisterForm,
    UserLoginForm,
    UserUpdateForm,
    UserChangePasswordForm,
    PasswordResetConfirmForm,
    PasswordResetForm,
    UserForm,
)
from users.services import (
    send_register_email,
    send_new_password_email,
    send_code_email,
)
from users.models import User


# ===== РЕГИСТРАЦИЯ И АВТОРИЗАЦИЯ =====

class UserRegisterView(CreateView):
    """Регистрация пользователя"""
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:user_login')
    template_name = 'users/register_update.html'
    extra_context = {'title': 'Создать аккаунт'}

    def form_valid(self, form):
        self.object = form.save()
        send_register_email(self.object.email)
        return super().form_valid(form)


class UserLoginView(LoginView):
    """Авторизация"""
    template_name = 'users/login.html'
    form_class = UserLoginForm
    extra_context = {'title': 'Авторизация'}


class UserLogoutView(LogoutView):
    """Выход"""
    template_name = 'users/logout.html'


# ===== ПРОФИЛЬ =====

class UserProfileView(LoginRequiredMixin, DetailView):
    """Профиль пользователя"""
    model = User
    form_class = UserForm
    template_name = 'users/user_profile_read_only.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        user_obj = self.get_object()
        context_data['title'] = f'Профиль: {user_obj}'
        return context_data


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля"""
    model = User
    form_class = UserUpdateForm
    template_name = 'users/register_update.html'
    success_url = reverse_lazy('users:user_profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        user_obj = self.get_object()
        context_data['title'] = f'Изменить профиль: {user_obj}'
        return context_data


class UserPasswordChangeView(PasswordChangeView):
    """Смена пароля"""
    form_class = UserChangePasswordForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:user_profile')
    extra_context = {'title': 'Изменить пароль'}


# ===== СПИСОК ПОЛЬЗОВАТЕЛЕЙ =====

class UserListView(LoginRequiredMixin, ListView):
    """Список пользователей"""
    model = User
    extra_context = {'title': 'Все пользователи'}
    template_name = 'users/users.html'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_active=True)


class UserDetailView(DetailView):
    """Детали пользователя"""
    model = User
    template_name = 'users/user_detail.html'

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        user_object = self.get_object()
        context_data['title'] = f'Профиль: {user_object}'
        return context_data


# ===== ВОССТАНОВЛЕНИЕ ПАРОЛЯ =====

def send_reset_code(request):
    """Отправка кода на email"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'users/password_reset.html', {
                    'form': form,
                    'error': 'Пользователь с таким email не найден'
                })

            code = ''.join(random.choices(string.digits, k=6))
            user.verification_code = code
            user.save()
            send_code_email(user.email, code)

            request.session['reset_email'] = email
            request.session['reset_code_sent'] = True

            return redirect('users:password_reset_confirm')
    else:
        form = PasswordResetForm()

    return render(request, 'users/password_reset.html', {'form': form})


def reset_password_confirm(request):
    """Подтверждение кода и смена пароля"""
    email = request.session.get('reset_email')

    if not email:
        return redirect('users:password_reset')

    if request.method == 'GET':
        if not request.session.get('reset_code_sent'):
            return redirect('users:password_reset')

        form = PasswordResetConfirmForm(initial={'email': email})
        return render(request, 'users/password_reset_confirm.html', {
            'form': form,
            'email': email
        })

    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                form.add_error(None, 'Пользователь не найден')
                return render(request, 'users/password_reset_confirm.html', {
                    'form': form, 'email': email
                })

            if user.verification_code != code:
                form.add_error('code', 'Неверный код подтверждения')
                return render(request, 'users/password_reset_confirm.html', {
                    'form': form, 'email': email
                })

            user.set_password(password)
            user.verification_code = None
            user.save()

            request.session.pop('reset_email', None)
            request.session.pop('reset_code_sent', None)

            messages.success(request, 'Пароль успешно изменён!')
            return redirect('users:user_login')

    return render(request, 'users/password_reset_confirm.html', {
        'form': PasswordResetConfirmForm(initial={'email': email}),
        'email': email
    })


def resend_code(request):
    """Повторная отправка кода"""
    email = request.session.get('reset_email')

    if not email:
        return redirect('users:password_reset')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('users:password_reset')

    code = ''.join(random.choices(string.digits, k=6))
    user.verification_code = code
    user.save()
    send_code_email(user.email, code)

    request.session['reset_code_sent'] = True

    messages.info(request, 'Новый код отправлен на вашу почту')
    return redirect('users:password_reset_confirm')