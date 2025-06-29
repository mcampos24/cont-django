from django.shortcuts import render
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma
from .idiomas import mensajes_por_idioma

def inicio(request):
    idioma_i = int(request.GET.get("idioma_i", 2))  # Español por defecto
    mensajes = mensajes_por_idioma(idioma_i)
    resultado = None

    if request.method == "POST":
        idioma_i = int(request.POST.get("idioma_i", idioma_i))
        mensajes = mensajes_por_idioma(idioma_i)
        texto_usuario = obtener_texto_desde_request(request)

        if texto_usuario.strip():
            idioma_detectado = detectar_idioma(texto_usuario, mensajes)
            resultado = analizar_texto(texto_usuario, mensajes)
            resultado["idioma"] = idioma_detectado
            
    return render(request, 'index.html', {
        "resultado": resultado,
        "mensajes": mensajes,
        "idioma_i": idioma_i
    })