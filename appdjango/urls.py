from django.urls import path #Esta funcion define rutas URL para Django
from . import views #Se importa el archivo anterior para realizar la conexion.

#muestra lo que definimos en views con la función incio (practicamente toda la pagina)
urlpatterns = [
    path('', views.inicio, name='inicio'),
]
#Es una URL vacia, es decir es la pagina principal, la cual va a tener todo lo del archivo anterior.

