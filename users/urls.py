from django.urls import path

from users.views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserUpdateView,
    UserPasswordChangeView,
    UserListView,
    UserDetailView,
    send_reset_code,
    reset_password_confirm,
    resend_code,
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('logout/', UserLogoutView.as_view(), name='user_logout'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', UserUpdateView.as_view(), name='user_update'),
    path('profile/password/', UserPasswordChangeView.as_view(), name='user_password_change'),
    path('users/', UserListView.as_view(), name='users_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('password-reset/', send_reset_code, name='password_reset'),
    path('password-reset/confirm/', reset_password_confirm, name='password_reset_confirm'),
    path('password-reset/resend/', resend_code, name='resend_code'),
]