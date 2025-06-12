from django.urls import path
from .views import busqueda_view

urlpatterns = [
    path('busqueda/', busqueda_view, name='busqueda'),
]

