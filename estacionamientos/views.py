# estacionamientos/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Estacionamiento, Reserva
from .forms import EstacionamientoForm, ReservaForm, CalificacionForm
from .decorators import solo_duenos
from .decorators import solo_clientes

@login_required
def listar_estacionamientos(request):
    """
    Lista todos los estacionamientos (podrías filtrar sólo disponibles, etc.).
    """
    estacionamientos = Estacionamiento.objects.all()
    return render(request, 'estacionamientos/listar_estacionamientos.html', {
        'estacionamientos': estacionamientos
    })

@solo_duenos
@login_required
def crear_estacionamiento(request):
    """
    Crea un estacionamiento asociado al usuario actual (asumiendo que es dueño).
    """
    if request.method == 'POST':
        form = EstacionamientoForm(request.POST)
        if form.is_valid():
            estacionamiento = form.save(commit=False)
            estacionamiento.owner = request.user
            estacionamiento.save()
            return redirect('listar_estacionamientos')
    else:
        form = EstacionamientoForm()
    return render(request, 'estacionamientos/crear_estacionamiento.html', {
        'form': form
    })

@login_required
def detalle_estacionamiento(request, pk):
    """
    Muestra los detalles de un estacionamiento en particular.
    """
    estacionamiento = get_object_or_404(Estacionamiento, pk=pk)
    return render(request, 'estacionamientos/detalle_estacionamiento.html', {
        'estacionamiento': estacionamiento
    })

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

@solo_clientes
@login_required
def crear_reserva(request, estacionamiento_id):
    estacionamiento = get_object_or_404(Estacionamiento, id=estacionamiento_id)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Asignar el estacionamiento al 'instance' para que lo use en clean()
        reserva = form.instance
        reserva.estacionamiento = estacionamiento
        reserva.cliente = request.user

        if form.is_valid():
            return redirect('detalle_reserva', pk=reserva.id)
    else:
        form = ReservaForm()
    return render(request, 'estacionamientos/crear_reserva.html', {
        'form': form,
        'estacionamiento': estacionamiento
    })

@login_required
def detalle_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    return render(request, 'estacionamientos/detalle_reserva.html', {
        'reserva': reserva
    })

@login_required
def reporte_transacciones(request):
    """
    Muestra, para un dueño, las reservas relacionadas a sus estacionamientos.
    """
    if not hasattr(request.user, 'rol') or request.user.rol != 'dueno':
        return redirect('listar_estacionamientos')
    estacionamientos_propios = Estacionamiento.objects.filter(owner=request.user)
    reservas_relacionadas = Reserva.objects.filter(estacionamiento__in=estacionamientos_propios)
    return render(request, 'estacionamientos/reporte_transacciones.html', {
        'reservas': reservas_relacionadas
    })

@login_required
def calificar_reserva(request, reserva_id):
    """
    Permite crear una calificacion si la reserva está confirmada.
    - El 'user_calificador' es el request.user
    - 'user_calificado' depende de si es un dueño o un cliente.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Validar estado
    if reserva.estado != 'Confirmada':
        # no se puede calificar todavía
        return redirect('detalle_reserva', pk=reserva_id)

    # Determinar a quién se califica. Por ejemplo:
    # - si request.user es el cliente, califica al dueño
    # - si request.user es el dueño, califica al cliente
    if request.user == reserva.cliente:
        user_calificado = reserva.estacionamiento.owner
    elif request.user == reserva.estacionamiento.owner:
        user_calificado = reserva.cliente
    else:
        # No involucrado en la reserva => no califica
        return redirect('listar_estacionamientos')

    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calif = form.save(commit=False)
            calif.reserva = reserva
            calif.user_calificador = request.user
            calif.user_calificado = user_calificado
            calif.save()
            return redirect('detalle_reserva', pk=reserva_id)
    else:
        form = CalificacionForm()

    return render(request, 'estacionamientos/calificar_reserva.html', {
        'form': form,
        'reserva': reserva,
    })


@login_required
def finalizar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    # Solo permitir que el dueño o el cliente finalicen
    if request.user not in [reserva.cliente, reserva.estacionamiento.owner]:
        return redirect('detalle_reserva', pk=pk)

    # O podrías chequear que la fecha actual sea >= fechaFin
    # from django.utils import timezone
    # if timezone.now() < reserva.fechaFin:
    #     return redirect('detalle_reserva', pk=pk)

    if reserva.estado == 'Confirmada':
        reserva.actualizarEstado('Finalizada')

    return redirect('detalle_reserva', pk=pk)

