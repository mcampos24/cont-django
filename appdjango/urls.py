from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
]
from django.contrib import admin
from .views import mostrar_detectar_idioma
urlpatterns=[
    path("admin/", admin.site.urls),
    path("",mostrar_detectar_idioma)
]
from .views import mostrar_analisis
urlpatterns=[
    path("admin/",admin.site.urls),
    path("",mostrar_analisis)
]
from .views import mostrar_palabra_mas_repetida
urlpatterns=[
    path("admin/",admin.site.urls),
    path("",mostrar_palabra_mas_repetida)
]
from .views import mostrar_frecuencia_porcentual
urlpatterns=[
    path("admin/",admin.site.urls),
    path("", mostrar_frecuencia_porcentual)
]
from .views import mostrar_varianza_poblacional
urlpatterns=[
    path("admin/",admin.site.urls),
    path("",mostrar_varianza_poblacional)
]
from .views import mostrar_sugerir_sinonimos
urlpatterns=[
    path("admin/",admin.site.urls),
    path("",mostrar_sugerir_sinonimos)
]

