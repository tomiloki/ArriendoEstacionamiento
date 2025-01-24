# users/forms.py

import re
from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            'username', 'password1', 'password2',
            'rol', 'rut', 'direccion',
            'cuenta_bancaria', 'tarjeta_credito', 'banco'
        )

    def clean_tarjeta_credito(self):
        numero = self.cleaned_data.get('tarjeta_credito')
        if numero:
            # Ejemplo: 16 dígitos, sin guiones
            if not re.match(r'^\d{16}$', numero):
                raise ValidationError("El número de tarjeta de crédito debe tener 16 dígitos.")
        return numero