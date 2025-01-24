# estacionamientos/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class Estacionamiento(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'dueno'},
        related_name='estacionamientos'
    )
    ubicacion = models.CharField(max_length=255)
    coordenadas = models.CharField(max_length=255)
    tarifa = models.FloatField()
    disponibilidad = models.BooleanField(default=True)
    accesoRemoto = models.BooleanField(default=False)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Estacionamiento #{self.id} - Dueño: {self.owner.username}"

class Reserva(models.Model):
    ESTADO_CHOICES = (
        ('Pendiente', 'Pendiente'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
        ('Finalizada', 'Finalizada'),
    )

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'cliente'},
        related_name='reservas'
    )
    estacionamiento = models.ForeignKey(
        Estacionamiento,
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    fechaInicio = models.DateTimeField()
    fechaFin = models.DateTimeField()
    tiempoExpiracion = models.IntegerField(default=0)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')

    def calcularCosto(self) -> float:
        duracion_horas = (self.fechaFin - self.fechaInicio).total_seconds() / 3600
        return round(duracion_horas * self.estacionamiento.tarifa, 2)

    def actualizarEstado(self, nuevoEstado: str):
        self.estado = nuevoEstado
        self.save()

    def __str__(self):
        return f"Reserva #{self.id} - {self.cliente.username}"

class Calificacion(models.Model):
    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='calificaciones'
    )
    puntuacion = models.PositiveSmallIntegerField()
    comentario = models.TextField(blank=True, null=True)
    user_calificado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones_recibidas'
    )
    user_calificador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='calificaciones_realizadas'
    )
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Calificación {self.puntuacion} - {self.user_calificado.username}"
