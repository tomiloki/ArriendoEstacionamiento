# estacionamientos/views.py
"""
Vistas para la app 'estacionamientos':

- listar_estacionamientos: Lista todos los estacionamientos (solo si rol='cliente' o rol='consultor').
- crear_estacionamiento: Creación de nuevos estacionamientos (solo rol='dueno').
- detalle_estacionamiento: Muestra detalles y permite habilitar/deshabilitar un estacionamiento (dueño).
- crear_reserva: Reserva un estacionamiento (solo rol='cliente'), validando fechas y solapamientos.
- detalle_reserva: Muestra el estado de la reserva, permitir pagos o calificaciones si aplica.
- reporte_transacciones: Genera reporte de reservas ligadas a un dueño.
- calificar_reserva: Permite calificar al dueño o al cliente tras finalizar la reserva (estado='Finalizada').
"""


from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Estacionamiento, Reserva
from .forms import EstacionamientoForm, ReservaForm, CalificacionForm
from .decorators import solo_duenos, solo_clientes

@login_required
@solo_clientes
def listar_estacionamientos(request):
    estacionamientos = list(Estacionamiento.objects.all().values('ubicacion', 'coordenadas', 'disponibilidad'))
    return render(request, 'estacionamientos/listar_estacionamientos.html', {
        'estacionamientos': estacionamientos,
        'google_maps_api_key': 'settings.   GOOGLE_MAPS_API_KEY'
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

        if form.is_valid():
            # form.is_valid() = True => Django ya procesó los datos y están correctos
            reserva = form.save(commit=False)
            reserva.cliente = request.user
            reserva.estacionamiento = estacionamiento
            reserva.save()  # Aquí se guarda y ya tenemos reserva.id
            
            # Redirigimos con el pk real
            return redirect('detalle_reserva', pk=reserva.pk)
        else:
            # Si el form no es válido, se vuelve a mostrar el template con errores
            return render(request, 'estacionamientos/crear_reserva.html', {
                'form': form,
                'estacionamiento': estacionamiento
            })
    else:
        # GET: mostrar formulario vacío
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
    if reserva.estado != 'Finalizada':
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


@login_required
@solo_duenos
def mis_reservas(request):
    """
    Muestra todas las reservas que hay en los estacionamientos
    cuyo dueño sea el usuario actual.
    """
    estacionamientos_propios = Estacionamiento.objects.filter(owner=request.user)
    # Filtra todas las reservas asociadas a esos estacionamientos.
    reservas = Reserva.objects.filter(estacionamiento__in=estacionamientos_propios)

    return render(request, 'estacionamientos/mis_reservas.html', {
        'reservas': reservas
    })
