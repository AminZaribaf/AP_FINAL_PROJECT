from django.urls import path
from .views import RegisterUserView, LoginUserView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    #
    path('register/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

