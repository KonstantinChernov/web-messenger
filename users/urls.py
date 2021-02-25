from django.urls import path
from .views import Register, UserLogin

urlpatterns = [
    path('', UserLogin.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
]
