# Arriendo de Estacionamientos

Proyecto Django MVC (MVT) para arrendar estacionamientos. Se contemplan cuatro roles:
- **Cliente**: busca y reserva estacionamientos.
- **Dueño**: registra nuevos estacionamientos, genera reportes de sus transacciones.
- **Administrador**: administra usuarios (bloquear, etc.).
- **Consultor**: consulta estacionamientos pero no reserva ni crea.

## Estructura


### Instrucciones
- `python manage.py migrate`
- `python manage.py runserver`
- Acceder a `http://127.0.0.1:8000/`
