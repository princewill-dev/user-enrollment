from django.urls import path
from .views import RegisterView, VerifyOTPView, ResendOTPView, CreatePasswordView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('create-password/', CreatePasswordView.as_view(), name='create_password'),
]
