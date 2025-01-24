# users/models.py

# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROL_CHOICES = (
        ('cliente', 'Cliente'),
        ('dueno', 'Dueño'),
        ('administrador', 'Administrador'),
        ('consultor', 'Consultor'),
    )
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')

    # Ejemplo de campos adicionales
    cuenta_bancaria = models.CharField(max_length=50, blank=True, null=True)
    tarjeta_credito = models.CharField(max_length=16, blank=True, null=True)
    banco = models.CharField(max_length=50, blank=True, null=True)
    rut = models.CharField(max_length=12, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.rol})"
