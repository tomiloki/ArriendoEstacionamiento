# pagos/urls.py

from django.urls import path
from .views import procesar_pago

urlpatterns = [
    path('procesar/<int:reserva_id>/', procesar_pago, name='procesar_pago'),
]
