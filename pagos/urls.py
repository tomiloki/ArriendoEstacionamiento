# pagos/urls.py

from django.urls import path
from .views import iniciar_pago, reporte_transacciones

urlpatterns = [
    path('iniciar/<int:reserva_id>/', iniciar_pago, name='iniciar_pago'),
    path('reporte-transacciones/', reporte_transacciones, name='reporte_transacciones'),

]
