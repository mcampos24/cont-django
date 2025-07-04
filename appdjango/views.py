from django.shortcuts import render
from .utils import obtener_texto_desde_request, analizar_texto, detectar_idioma, analizar_texto, palabra_mas_repetida, varianza_poblacional,sugerir_sinonimos
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
from .utils import detectar_idioma
def mostrar_detectar_idioma(request):
    detectaridioma = detectar_idioma()
    return render(request,"detectar_idioma.html",{"detectar_idioma":detectaridioma})
from .utils import analizar_texto
def mostrar_analisis(request):
    analisis = analizar_texto()
    return render(request,"analisis.html",{"analisis":analisis})
from .utils import palabra_mas_repetida
def mostrar_palabra_mas_repetida(request):
    palabramasrepetida = palabra_mas_repetida()
    return render(request,"palabra_mas_repetida",{"palabra_mas_repetida":palabramasrepetida})
from .utils import frecuencia_porcentual
def mostrar_frecuencia_porcentual(request):
    frecuenciaporcentual = frecuencia_porcentual()
    return render(request,"frecuencia_porcentual.html",{"frecuencia_porcentual":frecuenciaporcentual})
from .utils import varianza_poblacional
def mostrar_varianza_poblacional(request):
    varianzapoblacional=varianza_poblacional()
    return render(request,"varianza_poblacional.html",{"varianza_poblacional":varianzapoblacional})
from .utils import sugerir_sinonimos
def mostrar_sugerir_sinonimos(request):
    sugerirsinonimos = sugerir_sinonimos()
    return render(request,"sugerir_sinonimos.html",{"sugerir_sinonimos":sugerirsinonimos})