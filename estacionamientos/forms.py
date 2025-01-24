# estacionamientos/forms.py

import re
from django import forms
from .models import Estacionamiento, Reserva
from django.utils import timezone
from django.forms import DateInput
from .models import Calificacion

# estacionamientos/forms.py

class EstacionamientoForm(forms.ModelForm):
    class Meta:
        model = Estacionamiento
        fields = ['ubicacion', 'coordenadas', 'tarifa', 'accesoRemoto', 'tipo']

    def clean_tarifa(self):
        tarifa = self.cleaned_data.get('tarifa')
        if tarifa is not None and tarifa < 0:
            raise forms.ValidationError("La tarifa no puede ser negativa.")
        return tarifa
    
    def clean_coordenadas(self):
        coords = self.cleaned_data.get('coordenadas')
        # Ejemplo: esperamos algo tipo "LAT,LON" (solo números, punto, coma, espacios)
        # Este regex es muy simplificado, tú lo ajustas a tu realidad
        pattern = r'^-?\d+(\.\d+)?,\s*-?\d+(\.\d+)?$'
        if coords and not re.match(pattern, coords.strip()):
            raise forms.ValidationError("Formato de coordenadas inválido (use lat,lon).")
        return coords.strip()

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fechaInicio', 'fechaFin']
        widgets = {
            'fechaInicio': DateInput(attrs={'type': 'datetime-local'}),
            'fechaFin': DateInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fechaInicio')
        fecha_fin = cleaned_data.get('fechaFin')
        estacionamiento = self.instance.estacionamiento  # Se completará en la vista

        # 1) Verificar fechaFin > fechaInicio
        if fecha_inicio and fecha_fin:
            if fecha_fin <= fecha_inicio:
                raise forms.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")

        # 2) Verificar solapamientos
        # Buscamos reservas de ese estacionamiento que se crucen con el rango introducido
        # con estado 'Pendiente' o 'Confirmada' (asumiendo Canceladas no afectan).
        if fecha_inicio and fecha_fin and estacionamiento:
            overlapping = Reserva.objects.filter(
                estacionamiento=estacionamiento,
                estado__in=['Pendiente', 'Confirmada']
            ).exclude(pk=self.instance.pk).filter(
                fechaInicio__lt=fecha_fin,
                fechaFin__gt=fecha_inicio
            )
            if overlapping.exists():
                raise forms.ValidationError(
                    "Este estacionamiento ya está reservado en parte de ese rango horario."
                )
        return cleaned_data

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['puntuacion', 'comentario']
    
    def clean_puntuacion(self):
        p = self.cleaned_data['puntuacion']
        if p < 1 or p > 5:
            raise forms.ValidationError("La puntuación debe ser entre 1 y 5.")
        return p

