# Generated by Django 5.1.4 on 2025-01-24 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estacionamientos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estacionamiento',
            name='coordenadas',
        ),
        migrations.AddField(
            model_name='estacionamiento',
            name='lat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='estacionamiento',
            name='lng',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='estado',
            field=models.CharField(choices=[('Pendiente', 'Pendiente'), ('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada'), ('Finalizada', 'Finalizada')], default='Pendiente', max_length=10),
        ),
    ]
