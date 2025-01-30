from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import re

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Nombre de Usuario",
        help_text="Ingrese un nombre de usuario válido. Máximo 150 caracteres.",
        max_length=150,
        error_messages={
            'required': "Este campo es obligatorio.",
            'max_length': "El nombre de usuario no puede exceder los 150 caracteres."
        }
    )

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput,
        help_text="Debe tener al menos 8 caracteres, un número, una mayúscula y un carácter especial.",
        error_messages={
            'required': "Este campo es obligatorio."
        }
    )

    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput,
        error_messages={
            'required': "Este campo es obligatorio.",
            'invalid': "Las contraseñas no coinciden."
        }
    )

    rut = forms.CharField(
        label="RUT",
        help_text="Ingrese su RUT en formato válido (Ej: 12.345.678-9).",
        error_messages={
            'required': "Este campo es obligatorio."
        }
    )

    direccion = forms.CharField(
        label="Dirección",
        help_text="Ingrese su dirección completa (Calle, número, ciudad).",
        error_messages={
            'required': "Este campo es obligatorio."
        }
    )

    cuenta_bancaria = forms.CharField(
        label="Cuenta Bancaria",
        required=False,
        help_text="Ingrese su cuenta bancaria si es dueño.",
        error_messages={
            'required': "Debe ingresar su cuenta bancaria si es dueño."
        }
    )

    banco = forms.CharField(
        label="Banco",
        required=False,
        help_text="Ingrese el nombre de su banco si es dueño.",
        error_messages={
            'required': "Debe ingresar el nombre de su banco si es dueño."
        }
    )

    tarjeta_credito = forms.CharField(
        label="Tarjeta de Crédito",
        required=False,
        help_text="Ingrese su tarjeta de crédito si es cliente.",
        error_messages={
            'required': "Debe ingresar su tarjeta de crédito si es cliente."
        }
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'password1', 'password2',
            'rol', 'rut', 'direccion',
        )
        error_messages = {
            'password2': {
                'password_mismatch': "Las contraseñas no coinciden."
            }
        }

    def clean_rut(self):
        rut = self.cleaned_data.get("rut")
        if not re.match(r'^[0-9]+\.[0-9]+\.[0-9]+-[0-9kK]$', rut):
            raise forms.ValidationError("El RUT debe estar en formato válido (Ej: 12.345.678-9).")
        return rut

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("La contraseña debe incluir al menos un número.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("La contraseña debe incluir al menos una letra mayúscula.")
        if not any(char in "!@#$%^&*()-_=+{};:,<.>" for char in password):
            raise forms.ValidationError("La contraseña debe incluir al menos un carácter especial (!@#$%^&*).")
        if password.lower() in ['password', 'contraseña', '12345678', 'admin']:
            raise forms.ValidationError("La contraseña es demasiado común. Escoja otra.")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get("rol")

        if rol == "dueno":
            if not cleaned_data.get("cuenta_bancaria"):
                self.add_error("cuenta_bancaria", "Debe ingresar su cuenta bancaria si es dueño.")
            if not cleaned_data.get("banco"):
                self.add_error("banco", "Debe ingresar el nombre de su banco si es dueño.")

        if rol == "cliente":
            if not cleaned_data.get("tarjeta_credito"):
                self.add_error("tarjeta_credito", "Debe ingresar su tarjeta de crédito si es cliente.")
        
        return cleaned_data