from django.db import models
from estacionamientos.models import Reserva
from django.utils.timezone import now

class Pago(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20, 
        choices=[('Pendiente', 'Pendiente'), ('Completado', 'Completado'), ('Fallido', 'Fallido')],
        default='Pendiente'
    )
    fecha_pago = models.DateTimeField(auto_now_add=True)
    transaccion_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Pago {self.transaccion_id} - {self.estado}"
