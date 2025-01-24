# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test, login_required
from .models import CustomUser
from .forms import CustomUserCreationForm
from estacionamientos.decorators import solo_duenos, solo_clientes

@login_required
@solo_duenos
def home_dueno(request):
    """
    Muestra la pantalla principal (dashboard) del dueño,
    con enlaces y funcionalidad relevante sólo para el rol 'dueno'.
    """
    return render(request, 'home_dueno.html')

@login_required
@solo_clientes
def home_cliente(request):
    """
    Muestra la pantalla principal (dashboard) del cliente,
    con enlaces y funcionalidad relevante sólo para el rol 'cliente'.
    """
    return render(request, 'home_cliente.html')

def register(request):
    """
    Vista para registrar un nuevo usuario en el sistema.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loguea automáticamente al usuario registrado

            # Redirección según el rol del usuario
            if user.rol == 'dueno':  # Suponiendo que el modelo User tiene un campo `rol`
                return redirect('home_dueno')  # Cambia por la vista específica de "dueño"
            elif user.rol == 'cliente':
                return redirect('home_cliente')  # Cambia por la vista específica de "cliente"
            else:
                return redirect('listar_estacionamientos')  # Redirige a una vista genérica
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def bloquear_usuario(request, user_id):
    """
    Vista para que un administrador (superuser) bloquee a un usuario (dejándolo inactivo).
    """
    usuario = get_object_or_404(CustomUser, id=user_id)
    usuario.is_active = False
    usuario.save()
    return redirect('administracion_usuarios')  # Redirige a la administración de usuarios

@user_passes_test(lambda u: u.is_superuser)
def administracion_usuarios(request):
    """
    Vista que lista todos los usuarios y permite gestionar su estado.
    Solo accesible a superusuarios.
    """
    usuarios = CustomUser.objects.all()
    return render(request, 'users/administracion.html', {'usuarios': usuarios})
