from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
app_name = 'accounts'

urlpatterns = [
    path('auth/request-otp', views.RequestOPTView.as_view(), name='auth_request_otp'),
    path('auth/verify-otp', views.VerifyOTPView.as_view(), name='auth_verify_otp'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    #path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')

]