from django.shortcuts import render
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma

def inicio(request):
    resultado = None

    if request.method == "POST":
        texto_usuario = obtener_texto_desde_request(request)

        if texto_usuario.strip():
            idioma_detectado = detectar_idioma(texto_usuario)
            resultado = analizar_texto(texto_usuario)
            resultado["idioma"] = idioma_detectado

    return render(request, 'index.html', {"resultado": resultado})