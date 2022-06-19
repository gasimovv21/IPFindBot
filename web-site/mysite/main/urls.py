from django.urls import path, include
from . import views

urlpatterns = [
    path('ip-adresse/', views.show_client_ip),
]
