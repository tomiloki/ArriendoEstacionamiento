# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, bloquear_usuario, administracion_usuarios, home_dueno, home_cliente

urlpatterns = [
    path('dueno/home/', home_dueno, name='home_dueno'),
    path('cliente/home/', home_cliente, name='home_cliente'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('bloquear/<int:user_id>/', bloquear_usuario, name='bloquear_usuario'),
    path('administracion/', administracion_usuarios, name='administracion_usuarios'),
]
