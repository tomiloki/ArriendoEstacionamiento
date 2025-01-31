# estacionamientos/urls.py

from django.urls import path
from pagos.views import iniciar_pago
from .views import (
    listar_estacionamientos,
    listar_estacionamientos_dueno,  # ✅ Nuevo
    crear_estacionamiento,
    detalle_estacionamiento,
    toggle_estacionamiento,
    mis_reservas,
    reservas_dueno,
    crear_reserva,
    detalle_reserva,
    generar_recibo,
    editar_estacionamiento,
)

urlpatterns = [
    # Rutas para los clientes
    path('', listar_estacionamientos, name='listar_estacionamientos'),
    path('mis-reservas/', mis_reservas, name='mis_reservas'),
    
    # Rutas para los dueños
    path('mis/', listar_estacionamientos_dueno, name='listar_estacionamientos_dueno'),  # ✅ Nuevo
    path('reservas/', reservas_dueno, name='reservas_dueno'),
    path('nuevo/', crear_estacionamiento, name='crear_estacionamiento'),
    path('<int:pk>/', detalle_estacionamiento, name='detalle_estacionamiento'),
    path('toggle/<int:pk>/', toggle_estacionamiento, name='toggle_estacionamiento'),
    path('editar/<int:pk>/', editar_estacionamiento, name='editar_estacionamiento'),
    
    # Rutas de reservas
    path('reservar/<int:pk>/', crear_reserva, name='crear_reserva'),
    path('reserva/<int:pk>/', detalle_reserva, name='detalle_reserva'),

    
    # Rutas de pagos
    path('reserva/<int:pk>/pago/', iniciar_pago, name='iniciar_pago'),
    path('reserva/<int:pk>/recibo/', generar_recibo, name='generar_recibo'),
]
