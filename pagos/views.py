# pagos/views.py
from django.shortcuts import get_object_or_404, redirect
from estacionamientos.models import Reserva
from .models import Pago

def procesar_pago(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    # Verificar que el user sea quien reservo
    if request.user != reserva.cliente:
        return redirect('detalle_reserva', pk=reserva.id)

    # Crea o recupera el pago
    pago, created = Pago.objects.get_or_create(reserva=reserva, defaults={'monto': reserva.calcularCosto()})

    # Lógica: simular una aprobación o conectarse a una API
    pago.estado = 'aprobado'
    pago.save()
    # Reserva confirmada
    reserva.estado = 'Confirmada'
    reserva.save()
    return redirect('detalle_reserva', pk=reserva.id)
