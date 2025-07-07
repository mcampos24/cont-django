from __future__ import annotations
from django.shortcuts import render
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma, analizar_texto, generar_nube_palabras
from .idiomas import mensajes_por_idioma
import json

def inicio(request):
    idioma_i = int(request.GET.get("idioma_i", 2))  # Español por defecto
    mensajes = mensajes_por_idioma(idioma_i)
    resultado = None
    texto_usuario = ""

    # Inicializar variables para que no fallen si es GET
    labels_json = json.dumps([])
    data_json = json.dumps([])
    labels_pie = json.dumps([])
    data_pie = json.dumps([])

    if request.method == "POST":
        idioma_i = int(request.POST.get("idioma_i", idioma_i))
        mensajes = mensajes_por_idioma(idioma_i)
        texto_usuario = obtener_texto_desde_request(request)

        if texto_usuario.strip():
            generar_nube_palabras(texto_usuario)
            idioma_detectado = detectar_idioma(texto_usuario, mensajes)
            resultado = analizar_texto(texto_usuario, mensajes)
            resultado["idioma"] = idioma_detectado

            # Extraer datos para la gráfica de barras
            frecuencias = resultado.get("frecuencias_clasificadas", {})
            labels_json = json.dumps(list(frecuencias.keys()))
            data_json = json.dumps([valor.get("porcentaje", 0) for valor in frecuencias.values()])

            #Extraer datos para la gráfica de torat
            frecuencia_todas = resultado.get("frecuencia_todas", {})
            labels_pie = json.dumps(list(frecuencia_todas.keys()))
            data_pie = json.dumps(list(frecuencia_todas.values()))

            #Para la nube de palabras
            resultado["nube_path"] = "/static/img/nube.png"
            

    #Render se refiere a prácticamente lo que se va a mostrar entonces son todos los datos
    return render(request, 'index.html', {
    "resultado": resultado,
    "mensajes": mensajes,
    "idioma_i": idioma_i,
    "labels_json": labels_json,
    "data_json": data_json,
    "labels_pie": labels_pie,
    "data_pie": data_pie,})





