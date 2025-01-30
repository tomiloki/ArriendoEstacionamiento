import requests
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Estacionamiento, Reserva
from .forms import EstacionamientoForm, ReservaForm, CalificacionForm
from .decorators import solo_duenos, solo_clientes
import json
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.mail import send_mail

@login_required
@solo_clientes
def listar_estacionamientos(request):
    """
    Muestra todos los estacionamientos disponibles en un mapa interactivo.
    """
    estacionamientos = Estacionamiento.objects.filter(disponibilidad=True)

    estacionamientos_list = [
        {
            "id": est.id if est.id else None,
            "ubicacion": est.ubicacion,
            "coordenadas": est.coordenadas if est.coordenadas else None,
            "tarifa": est.tarifa,
            "detalle_url": reverse("detalle_estacionamiento", args=[est.id]) if est.id else "#"
        }
        for est in estacionamientos if est.id
    ]

    return render(request, "estacionamientos/listar_estacionamientos.html", {
        "estacionamientos": estacionamientos,  # ✅ Asegurar que se pasa al template
        "estacionamientos_json": json.dumps(estacionamientos_list),
        "google_maps_key": settings.GOOGLE_MAPS_API_KEY,
    })




# 🏗️ CREAR ESTACIONAMIENTO
@login_required
@solo_duenos
def crear_estacionamiento(request):
    if request.method == 'POST':
        form = EstacionamientoForm(request.POST)
        if form.is_valid():
            estacionamiento = form.save(commit=False)
            estacionamiento.owner = request.user
            estacionamiento.coordenadas = request.POST.get("coordenadas", "")
            estacionamiento.save()
            messages.success(request, "Estacionamiento creado con éxito.")
            return redirect('listar_estacionamientos')
    else:
        form = EstacionamientoForm()
    return render(request, 'estacionamientos/crear_estacionamiento.html', {
        'form': form,
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
    })

# 🏢 DETALLE ESTACIONAMIENTO
@login_required
def detalle_estacionamiento(request, pk):
    """
    Muestra los detalles de un estacionamiento en particular.
    """
    estacionamiento = get_object_or_404(Estacionamiento, pk=pk)
    
    # Asegurémonos de que se envíen las coordenadas
    coordenadas = estacionamiento.coordenadas.split(',') if estacionamiento.coordenadas else ['-33.4489', '-70.6693']

    return render(request, 'estacionamientos/detalle_estacionamiento.html', {
        'estacionamiento': estacionamiento,
        'lat': coordenadas[0],
        'lng': coordenadas[1],
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
    })


# ✅ HABILITAR/DESHABILITAR ESTACIONAMIENTO
@login_required
def habilitar_estacionamiento(request, pk):
    estacionamiento = get_object_or_404(Estacionamiento, pk=pk)
    if estacionamiento.owner == request.user:
        estacionamiento.disponibilidad = True
        estacionamiento.save()
    return redirect('detalle_estacionamiento', pk=pk)

@login_required
def deshabilitar_estacionamiento(request, pk):
    estacionamiento = get_object_or_404(Estacionamiento, pk=pk)
    if estacionamiento.owner == request.user:
        estacionamiento.disponibilidad = False
        estacionamiento.save()
    return redirect('detalle_estacionamiento', pk=pk)

# 📅 CREAR RESERVA (SOLO CLIENTES)
@login_required
@solo_clientes
def crear_reserva(request, estacionamiento_id):
    """
    Permite a un cliente reservar un estacionamiento si está disponible y la fecha es válida.
    """
    estacionamiento = get_object_or_404(Estacionamiento, id=estacionamiento_id)

    if not estacionamiento.disponibilidad:
        messages.error(request, "Este estacionamiento no está disponible para reservas.")
        return redirect('detalle_estacionamiento', pk=estacionamiento.id)

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.cliente = request.user
            reserva.estacionamiento = estacionamiento

            overlapping = Reserva.objects.filter(
                estacionamiento=estacionamiento,
                estado__in=['Pendiente', 'Confirmada']
            ).exclude(pk=reserva.pk).filter(
                fechaInicio__lt=reserva.fechaFin,
                fechaFin__gt=reserva.fechaInicio
            )
            if overlapping.exists():
                messages.error(request, "Este estacionamiento ya tiene reservas en ese horario.")
                return redirect('crear_reserva', estacionamiento_id=estacionamiento.id)

            reserva.save()
            messages.success(request, "¡Reserva creada con éxito!")
            return redirect('detalle_reserva', pk=reserva.pk)

    else:
        form = ReservaForm()

    # 🔹 Convertimos coordenadas en variables separadas
    coordenadas = estacionamiento.coordenadas.split(",") if estacionamiento.coordenadas else ["-33.4489", "-70.6693"]
    lat = float(coordenadas[0])
    lng = float(coordenadas[1])

    return render(request, 'estacionamientos/crear_reserva.html', {
        'form': form,
        'estacionamiento': estacionamiento,
        'tarifa': float(estacionamiento.tarifa) if estacionamiento.tarifa else 0.00,
        'lat': lat,  # 🔥 Mandamos latitud
        'lng': lng,  # 🔥 Mandamos longitud
        'google_maps_key': settings.GOOGLE_MAPS_API_KEY,
    })


# 🔍 DETALLE DE RESERVA
@login_required
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'estacionamientos/detalle_reserva.html', {
        'reserva': reserva
    })

# 📊 REPORTE DE TRANSACCIONES
@login_required
@solo_duenos
def reporte_transacciones(request):
    """
    Muestra, para un dueño, las reservas relacionadas a sus estacionamientos.
    """
    estacionamientos_propios = Estacionamiento.objects.filter(owner=request.user)
    reservas_relacionadas = Reserva.objects.filter(estacionamiento__in=estacionamientos_propios)
    return render(request, 'estacionamientos/reporte_transacciones.html', {
        'reservas': reservas_relacionadas
    })

# ⭐ CALIFICAR RESERVA (DUEÑO/CLIENTE)
@login_required
def calificar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado != 'Finalizada':
        return redirect('detalle_reserva', pk=reserva_id)

    if request.user == reserva.cliente:
        user_calificado = reserva.estacionamiento.owner
    elif request.user == reserva.estacionamiento.owner:
        user_calificado = reserva.cliente
    else:
        return redirect('listar_estacionamientos')

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save(commit=False)
            calificacion.reserva = reserva
            calificacion.user_calificador = request.user
            calificacion.user_calificado = user_calificado
            calificacion.save()
            messages.success(request, "Calificación registrada con éxito.")
            return redirect('detalle_reserva', pk=reserva_id)
    else:
        form = CalificacionForm()

    return render(request, 'estacionamientos/calificar_reserva.html', {
        'form': form,
        'reserva': reserva,
    })

# ⏳ FINALIZAR RESERVA
@login_required
def finalizar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)

    if request.user not in [reserva.cliente, reserva.estacionamiento.owner]:
        return redirect('detalle_reserva', pk=pk)

    if reserva.estado == 'Confirmada':
        reserva.estado = 'Finalizada'
        reserva.save()
        messages.success(request, "Reserva finalizada con éxito.")

    return redirect('detalle_reserva', pk=pk)

# 📌 MIS RESERVAS (SOLO PARA DUEÑOS)
@login_required
@solo_clientes
def mis_reservas(request):
    """
    Muestra todas las reservas del cliente actual.
    """
    reservas = Reserva.objects.filter(cliente=request.user).order_by('-fechaInicio')
    
    return render(request, 'estacionamientos/mis_reservas.html', {
        'reservas': reservas
    })
    
@login_required
@solo_clientes
def cancelar_reserva(request, reserva_id):
    """
    Permite al cliente cancelar su reserva si aún está en estado 'Pendiente'.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if reserva.estado == "Pendiente":
        reserva.estado = "Cancelada"
        reserva.save()
        messages.success(request, "Reserva cancelada con éxito.")
    else:
        messages.error(request, "No puedes cancelar esta reserva.")

    return redirect('mis_reservas')

@login_required
@solo_clientes
def pagar_reserva(request, reserva_id):
    """
    Permite realizar el pago de una reserva confirmada.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if reserva.estado != "Confirmada":
        messages.error(request, "Solo puedes pagar reservas confirmadas.")
        return redirect('mis_reservas')

    if request.method == "POST":
        # Aquí iría la lógica de integración con la pasarela de pago
        reserva.estado = "Pagada"
        reserva.save()
        messages.success(request, "Pago realizado con éxito.")
        return redirect('detalle_reserva', pk=reserva.id)

    return render(request, 'estacionamientos/pagar_reserva.html', {
        'reserva': reserva
    })
    
@login_required
@solo_clientes
def generar_recibo(request, reserva_id):
    """
    Genera un recibo en formato PDF para la reserva pagada.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if reserva.estado != "Pagada":
        messages.error(request, "Solo puedes generar recibos de reservas pagadas.")
        return redirect('detalle_reserva', pk=reserva.id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Recibo_Reserva_{reserva.id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Recibo de Pago - Arriendo de Estacionamiento")

    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Reserva ID: {reserva.id}")
    p.drawString(100, 750, f"Cliente: {reserva.cliente.username}")
    p.drawString(100, 730, f"Estacionamiento: {reserva.estacionamiento.ubicacion}")
    p.drawString(100, 710, f"Fecha de Inicio: {reserva.fechaInicio}")
    p.drawString(100, 690, f"Fecha de Fin: {reserva.fechaFin}")
    p.drawString(100, 670, f"Total Pagado: ${reserva.estacionamiento.tarifa}")

    p.drawString(100, 640, "¡Gracias por usar nuestro servicio!")

    p.showPage()
    p.save()
    return response

def enviar_notificacion_pago(reserva):
    """
    Envía una notificación por email al cliente después de pagar.
    """
    asunto = "Pago Confirmado - Reserva de Estacionamiento"
    mensaje = f"""
    ¡Hola {reserva.cliente.username}!
    
    Tu pago para la reserva #{reserva.id} ha sido recibido con éxito.
    
    Detalles de la reserva:
    - Estacionamiento: {reserva.estacionamiento.ubicacion}
    - Fecha Inicio: {reserva.fechaInicio}
    - Fecha Fin: {reserva.fechaFin}
    - Monto: ${reserva.estacionamiento.tarifa}

    Puedes descargar tu recibo en la plataforma.

    ¡Gracias por confiar en nosotros!
    """

    send_mail(asunto, mensaje, 'no-reply@arriendoestacionamiento.com', [reserva.cliente.email])


@login_required
@solo_clientes
def pagar_reserva(request, reserva_id):
    """
    Permite realizar el pago de una reserva confirmada.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user)

    if reserva.estado != "Confirmada":
        messages.error(request, "Solo puedes pagar reservas confirmadas.")
        return redirect('mis_reservas')

    if request.method == "POST":
        reserva.estado = "Pagada"
        reserva.save()

        # Enviar notificación por email
        enviar_notificacion_pago(reserva)

        messages.success(request, "Pago realizado con éxito. Recibirás una confirmación por email.")
        return redirect('detalle_reserva', pk=reserva.id)

    return render(request, 'estacionamientos/pagar_reserva.html', {
        'reserva': reserva
    })
    
@login_required
def reservas_dueno(request):
    """
    Vista para que un dueño vea todas las reservas de sus estacionamientos.
    """
    estacionamientos = Estacionamiento.objects.filter(owner=request.user)
    reservas = Reserva.objects.filter(estacionamiento__in=estacionamientos).order_by('-fechaInicio')

    return render(request, 'estacionamientos/reservas_dueno.html', {
        'reservas': reservas
    })



