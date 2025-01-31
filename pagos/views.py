from django.shortcuts import render, redirect
from django.conf import settings
from django.urls import reverse
from .utils.webpay import WebpayService
from .models import Pago, Reserva
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from estacionamientos.models import Estacionamiento

def iniciar_pago(request, reserva_id):
    reserva = Reserva.objects.get(id=reserva_id)
    webpay = WebpayService()

    # URL de retorno después del pago
    url_retorno = request.build_absolute_uri(reverse("confirmar_pago"))

    # Iniciar transacción con Webpay
    response = webpay.iniciar_pago(
        monto=reserva.calcular_total(),
        orden_compra=f"reserva_{reserva.id}",
        url_retorno=url_retorno,
        url_final=settings.WEBPAY_FINAL_URL
    )

    if "url" in response:
        return redirect(response["url"] + "?token_ws=" + response["token"])
    else:
        messages.error(request, "Hubo un problema al procesar el pago.")
        return redirect("detalle_reserva", pk=reserva.id)

def confirmar_pago(request):
    token_ws = request.GET.get("token_ws")
    webpay = WebpayService()
    response = webpay.confirmar_pago(token_ws)

    if response["status"] == "AUTHORIZED":
        reserva_id = int(response["buy_order"].split("_")[1])
        reserva = Reserva.objects.get(id=reserva_id)

        # Registrar pago en la base de datos
        Pago.objects.create(
            reserva=reserva,
            monto=reserva.calcular_total(),
            estado="Pagado",
            transaccion_id=response["transaction_id"]
        )

        reserva.estado = "Confirmada"
        reserva.save()

        messages.success(request, "Pago realizado con éxito.")
        return redirect("detalle_reserva", pk=reserva.id)
    else:
        messages.error(request, "El pago no fue aprobado.")
        return redirect("mis_reservas")
    
@login_required
def reporte_transacciones(request):
    """
    Genera un reporte de transacciones para el dueño de estacionamientos.
    """
    # Filtrar los estacionamientos del dueño
    estacionamientos = Estacionamiento.objects.filter(owner=request.user)

    # Filtrar pagos asociados a estos estacionamientos
    pagos = Pago.objects.filter(reserva__estacionamiento__in=estacionamientos).order_by('-fecha_pago')

    return render(request, 'pagos/reporte_transacciones.html', {
        'pagos': pagos
    })

