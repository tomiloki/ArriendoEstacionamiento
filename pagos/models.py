# pagos/models.py

from django.db import models
from django.utils import timezone
from estacionamientos.models import Reserva
import requests
from django.conf import settings

class Pago(models.Model):
    ESTADO_PAGO = (
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    )

    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='pago')
    monto = models.FloatField()
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO, default='pendiente')
    fechaPago = models.DateTimeField(default=timezone.now)

    def procesarPago(self):
        """
        Lógica real o placeholder de integración con la pasarela/banco.
        """
        # Supón que tenemos una URL de API que aprueba el pago
        # (En la vida real, habría credenciales, tokens, etc.)
        api_url = "https://api.banco.com/realizar_pago/"
        payload = {
            'numero_tarjeta': self.reserva.cliente.tarjeta_credito,
            'monto': self.monto,
            'descripcion': f"Reserva #{self.reserva.id}",
        }
        try:
            response = requests.post(api_url, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Ej: {"status": "APROBADO"} o {"status": "RECHAZADO"}
                if data.get('status') == "APROBADO":
                    self.estado = 'aprobado'
                    self.save()
                    return True
                else:
                    self.estado = 'rechazado'
                    self.save()
                    return False
            else:
                # Error HTTP en la API => tratar como rechazo
                self.estado = 'rechazado'
                self.save()
                return False
        except requests.RequestException:
            # Error de conexión => tratar como rechazo
            self.estado = 'rechazado'
            self.save()
            return False

    def __str__(self):
        return f"Pago #{self.id} - Reserva #{self.reserva_id}"
