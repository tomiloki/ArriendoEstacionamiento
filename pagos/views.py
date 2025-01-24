# pagos/views.py

from django.shortcuts import get_object_or_404, redirect
from estacionamientos.models import Reserva
from .models import Pago
import random

def procesar_pago(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.user != reserva.cliente:
        return redirect('detalle_reserva', pk=reserva_id)

    # Crear o recuperar objeto Pago
    pago, created = Pago.objects.get_or_create(
        reserva=reserva,
        defaults={'monto': reserva.calcularCosto()}
    )

    # Llamar a la pasarela real
    aprobado = pago.procesarPago()
    if aprobado:
        reserva.actualizarEstado("Confirmada")
    else:
        # Podrías cancelar la reserva si hay rechazo
        reserva.actualizarEstado("Cancelada")

    return redirect('detalle_reserva', pk=reserva_id)