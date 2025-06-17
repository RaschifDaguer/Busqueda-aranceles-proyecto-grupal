from django.urls import path
from .views import busqueda_view, busqueda_avanzada, autocompletar_arancel, busqueda_codigo, busqueda_descripcion, autocompletar_codigo, autocompletar_descripcion, busqueda_combinada, login_view, logout_view
from . import views

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('busqueda/', busqueda_view, name='busqueda'),
    path('busqueda-avanzada/', busqueda_avanzada, name='busqueda_avanzada'),
    path('autocompletar-arancel/', autocompletar_arancel, name='autocompletar_arancel'),
    path('busqueda-codigo/', busqueda_codigo, name='busqueda_codigo'),
    path('busqueda-descripcion/', busqueda_descripcion, name='busqueda_descripcion'),
    path('autocompletar-codigo/', autocompletar_codigo, name='autocompletar_codigo'),
    path('autocompletar-descripcion/', autocompletar_descripcion, name='autocompletar_descripcion'),
    path('busqueda-combinada/', busqueda_combinada, name='busqueda_combinada'),
    path('aranceles/', views.aranceles_panel, name='aranceles'),
    path('aranceles/create/', views.arancel_create, name='arancel_create'),
    path('aranceles/<int:pk>/edit/', views.arancel_edit, name='arancel_edit'),
    path('aranceles/<int:pk>/delete/', views.arancel_delete, name='arancel_delete'),
    path('aranceles/form/', views.arancel_form, name='arancel_form'),
    path('aranceles/<int:pk>/form/', views.arancel_form, name='arancel_form_edit'),
    path('despachantes/', views.despachantes_panel, name='despachantes_panel'),
    path('despachantes/create/', views.despachante_create, name='despachante_create'),
    path('despachantes/<int:pk>/delete/', views.despachante_delete, name='despachante_delete'),
    path('historial/', views.historial_panel, name='historial_panel'),
]

