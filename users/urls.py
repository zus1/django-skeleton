from django.urls import path
from users import views

urlpatterns = [
    path('register', views.Register.as_view(), name='register'),
    path('login', views.Login.as_view(), name='login'),
    path('magic-link/send', views.MagicLinkSend.as_view(), name='magic-link-send'),
    path('magic-link/login', views.MagicLinkLogin.as_view(), name='magic-link-login'),
    path('logout', views.Logout.as_view(), name='logout'),
    path('reset-password/send', views.ResetPasswordSend.as_view(), name='reset-password-send'),
    path('reset-password', views.ResetPassword.as_view(), name='reset-password'),
    path('verify', views.Verify.as_view(), name='verify'),
    path('verify/resend', views.VerifyResend.as_view(), name='verify-resend'),
    path('me', views.Me.as_view(), name='me'),
    path('me/avatar', views.MeAvatar.as_view(), name='me-avatar'),
]