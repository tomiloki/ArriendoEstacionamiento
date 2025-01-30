# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, bloquear_usuario, administracion_usuarios, home_dueno, home_cliente, bienvenida, login_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('bloquear/<int:user_id>/', bloquear_usuario, name='bloquear_usuario'),
    path('administracion/', administracion_usuarios, name='administracion_usuarios'),
    path('bienvenida/', bienvenida, name='bienvenida'),
]
