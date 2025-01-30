# estacionamientos/urls.py

from django.urls import path
from .views import (
    listar_estacionamientos, crear_estacionamiento, detalle_estacionamiento,
    habilitar_estacionamiento, deshabilitar_estacionamiento,
    crear_reserva, detalle_reserva, reporte_transacciones,
    calificar_reserva, finalizar_reserva, mis_reservas, reservas_dueno
)

urlpatterns = [
    path('', listar_estacionamientos, name='listar_estacionamientos'),
    path('nuevo/', crear_estacionamiento, name='crear_estacionamiento'),
    path('<int:pk>/', detalle_estacionamiento, name='detalle_estacionamiento'),
    path('<int:pk>/habilitar/', habilitar_estacionamiento, name='habilitar_estacionamiento'),
    path('<int:pk>/deshabilitar/', deshabilitar_estacionamiento, name='deshabilitar_estacionamiento'),
    path('reserva/nuevo/<int:estacionamiento_id>/', crear_reserva, name='crear_reserva'),
    path('reserva/<int:pk>/', detalle_reserva, name='detalle_reserva'),
    path('reporte/', reporte_transacciones, name='reporte_transacciones'),
    path('reserva/calificar/<int:reserva_id>/', calificar_reserva, name='calificar_reserva'),
    path('reserva/finalizar/<int:pk>/', finalizar_reserva, name='finalizar_reserva'),
    path('mis-reservas/', mis_reservas, name='mis_reservas'),
    path('reservas/dueno/', reservas_dueno, name='reservas_dueno'),


]
