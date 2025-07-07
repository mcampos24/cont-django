from django.urls import path
from . import views

#muestra lo que definimos en views con la función incio (practicamente toda la pagina)
urlpatterns = [
    path('', views.inicio, name='inicio'),
]

