# Generated by Django 5.1.4 on 2025-01-24 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estacionamientos', '0002_remove_estacionamiento_coordenadas_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estacionamiento',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='estacionamiento',
            name='lng',
        ),
        migrations.AddField(
            model_name='estacionamiento',
            name='coordenadas',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
