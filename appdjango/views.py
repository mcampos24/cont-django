from __future__ import annotations
from django.shortcuts import render
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma, analizar_texto, palabra_mas_repetida, varianza_poblacional,sugerir_sinonimos
from .idiomas import mensajes_por_idioma
import json

def inicio(request):
    idioma_i = int(request.GET.get("idioma_i", 2))  # Español por defecto
    mensajes = mensajes_por_idioma(idioma_i)
    resultado = None
    texto_usuario = ""
    labels_json = []
    data_json = []

    if request.method == "POST":
        idioma_i = int(request.POST.get("idioma_i", idioma_i))
        mensajes = mensajes_por_idioma(idioma_i)
        texto_usuario = obtener_texto_desde_request(request)

        if texto_usuario.strip():
            idioma_detectado = detectar_idioma(texto_usuario, mensajes)
            resultado = analizar_texto(texto_usuario, mensajes)
            resultado["idioma"] = idioma_detectado

            # Extraer datos para la gráfica
            frecuencias = resultado.get("frecuencias_clasificadas", {})
            labels_json = json.dumps(list(frecuencias.keys()))
            data_json = json.dumps([valor.get("porcentaje", 0) for valor in frecuencias.values()])

    return render(request, 'index.html', {
    "resultado": resultado,
    "mensajes": mensajes,
    "idioma_i": idioma_i,
    "labels_json": labels_json,
    "data_json": data_json,})





