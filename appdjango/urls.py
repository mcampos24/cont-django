from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
]
from django.urls import path

from .views import analizar_texto_view

# Cada entrada: path(ruta, vista, nombre_opcional)
urlpatterns = [
    path("", analizar_texto_view, name="analizar"),  # raíz de la app
]


