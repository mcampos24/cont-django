from __future__ import annotations
from django.shortcuts import render # Esta es la funcion que genera una respuesta en el HTML
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma, analizar_texto, generar_nube_palabras
from .idiomas import mensajes_por_idioma #Se importan los demas archivos con los que se va a trabajar.
import json #Ayuda a convertir listas o diccionarios a texto en formato JSON

def inicio(request): #Función que se activa cuando alguien entra a la pagina principal
    idioma_i = int(request.GET.get("idioma_i", 2))  # Español por defecto
    mensajes = mensajes_por_idioma(idioma_i)
    resultado = None
    texto_usuario = ""

    # Inicializar variables para que no fallen si es GET
    labels_json = json.dumps([])
    data_json = json.dumps([])
    labels_pie = json.dumps([])
    data_pie = json.dumps([])

    if request.method == "POST": #Se ejecuta esto si se envia un texto
        idioma_i = int(request.POST.get("idioma_i", idioma_i))
        mensajes = mensajes_por_idioma(idioma_i) #Se vuelve a obtener el idioma, pero desde el texto.
        texto_usuario = obtener_texto_desde_request(request) #Se extrae el texto que ha escrito la persona.

        if texto_usuario.strip(): #Se verifica que el texto no este vacio
            
            idioma_detectado = detectar_idioma(texto_usuario, mensajes)
            generar_nube_palabras(texto_usuario, idioma_detectado) #Se crea una imagen como nube de palabras
            resultado = analizar_texto(texto_usuario, mensajes)
            resultado["idioma"] = idioma_detectado #Se realiza el analisis del texto.

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





