# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from .models import CustomUser
from .forms import CustomUserCreationForm

def register(request):
    """
    Vista para registrar un nuevo usuario en el sistema.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('listar_estacionamientos')  # Redirige a la vista deseada
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
