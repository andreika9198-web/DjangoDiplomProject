from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm, UserCreationForm, AuthenticationForm
)
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation

from users.models import User
from users.validators import validate_password


class StyleFormMixin:
    """Миксин для добавления Bootstrap-стилей"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class UserForm(StyleFormMixin, forms.ModelForm):
    """Базовая форма редактирования профиля"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'avatar')


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Форма регистрации"""
    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        cleaned_data = self.cleaned_data
        validate_password(cleaned_data['password1'])
        if cleaned_data['password1'] != cleaned_data['password2']:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data['password2']


class UserLoginForm(StyleFormMixin, AuthenticationForm):
    """Форма входа"""
    pass


class UserUpdateForm(UserForm):
    """Форма редактирования профиля (с vk_id)"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone',
                  'vk_id', 'avatar')   # ← vk_id вместо telegram/max


class UserChangePasswordForm(StyleFormMixin, PasswordChangeForm):
    """Смена пароля"""
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        validate_password(password1)
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        password_validation.validate_password(password2, self.user)
        return password2


class PasswordResetForm(StyleFormMixin, forms.Form):
    """Форма для ввода email при сбросе пароля"""
    email = forms.EmailField(label='Email')


class PasswordResetConfirmForm(forms.Form):
    """Подтверждение кода и новый пароль"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'readonly': 'readonly'})
    )
    code = forms.CharField(label='Код подтверждения', max_length=6)
    password = forms.CharField(
        label='Новый пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Повторите пароль', widget=forms.PasswordInput)

    def clean_password2(self):
        cd = self.cleaned_data
        validate_password(cd.get('password'))
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Ошибка! Пароли не совпадают')
        return cd.get('password2')