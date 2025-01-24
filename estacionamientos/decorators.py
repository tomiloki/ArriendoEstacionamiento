# estacionamientos/decorators.py

from django.shortcuts import redirect
from functools import wraps

def solo_duenos(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'dueno':
            return function(request, *args, **kwargs)
        return redirect('listar_estacionamientos')  # o mostrar error
    return wrap

# estacionamientos/decorators.py

def solo_clientes(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.rol == 'cliente':
            return function(request, *args, **kwargs)
        return redirect('listar_estacionamientos')
    return wrap
