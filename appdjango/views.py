from __future__ import annotations
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


import json
import os
import string
from typing import Dict, List

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from PyPDF2 import PdfReader
from fugashi import Tagger

# ---------------------------------------------------------------------------
#  Carga de sinónimos (espera un «sinonimos.json» con la estructura
#  {"español": {"verbo": ["…", …], "sustantivo": ["…", …]}, …}
# ---------------------------------------------------------------------------
SYN_PATH = os.path.join(settings.BASE_DIR, "idiomas", "sinonimos.json")
try:
    with open(SYN_PATH, "r", encoding="utf-8") as f:
        SINONIMOS: Dict[str, Dict[str, List[str]]] = json.load(f)
except FileNotFoundError:
    SINONIMOS = {}

# ---------------------------------------------------------------------------
#  Utilidades de E/S
# ---------------------------------------------------------------------------

def leer_texto_manual(texto: str) -> str:
    return texto.strip()


def leer_archivo_txt(file_obj) -> str:
    return file_obj.read().decode("utf-8", errors="ignore")


def leer_pdf(file_obj) -> str:
    texto = ""
    pdf = PdfReader(file_obj)
    for page in pdf.pages:
        texto += page.extract_text() or ""
    return texto


def obtener_texto_desde_request(request: HttpRequest) -> str:
    """Devuelve texto a analizar: "escribir" => textarea, "archivo" => upload."""
    modo = request.POST.get("modo")

    if modo == "escribir":
        return leer_texto_manual(request.POST.get("texto", ""))

    if modo == "archivo":
        archivo = request.FILES.get("archivo")
        if archivo:
            nombre = archivo.name.lower()
            if nombre.endswith(".txt"):
                return leer_archivo_txt(archivo)
            if nombre.endswith(".pdf"):
                return leer_pdf(archivo)
    return ""

# ---------------------------------------------------------------------------
#  Mensajes y constantes
# ---------------------------------------------------------------------------
DEFAULT_MESSAGES = {
    "y": "aparece",
    "z": "y es extremadamente frecuente",
    "a": "y es bastante frecuente",
    "b": "y tiene frecuencia moderada",
    "d": "y es poco frecuente",
    "e": "El texto es muy homogéneo (varianza baja)",
    "f": "El texto tiene una variabilidad moderada",
    "g": "El texto es muy disperso (varianza alta)",
    "no": "No se pudo detectar el idioma",
}

# ---------------------------------------------------------------------------
#  Detección de idioma
# ---------------------------------------------------------------------------

def detectar_idioma(texto: str, mensajes: Dict[str, str] | None = None) -> str:
    mensajes = mensajes or DEFAULT_MESSAGES
    texto = texto.lower()

    archivos_idioma = {
        "español": "español.txt",
        "portugues": "portugues.txt",
        "japones": "japones.txt",
        "ingles": "ingles.txt",
    }

    puntaje = {idioma: 0 for idioma in archivos_idioma}

    for idioma, archivo in archivos_idioma.items():
        ruta = os.path.join(settings.BASE_DIR, "idiomas", archivo)
        if not os.path.exists(ruta):
            continue
        with open(ruta, "r", encoding="utf-8") as f:
            palabras = f.read().lower().split()
        for p in palabras:
            puntaje[idioma] += texto.count(p)

    if all(v == 0 for v in puntaje.values()):
        return mensajes["no"]
    return max(puntaje, key=puntaje.get)

# ---------------------------------------------------------------------------
#  Métricas auxiliares
# ---------------------------------------------------------------------------

def palabra_mas_repetida(top: Dict[str, int]) -> str:
    return next(iter(top)) if top else ""


def frecuencia_porcentual(top: Dict[str, int], total: int, mensajes: Dict[str, str]) -> Dict[str, str]:
    res: Dict[str, str] = {}
    for palabra, freq in top.items():
        pct = round(freq / total * 100, 2) if total else 0
        if pct >= 30:
            txt = mensajes["z"]
        elif pct >= 15:
            txt = mensajes["a"]
        elif pct >= 5:
            txt = mensajes["b"]
        else:
            txt = mensajes["d"]
        res[palabra] = f"{palabra} {mensajes['y']} {pct}% {txt}"
    return res


def varianza_poblacional(freqs: List[int], mensajes: Dict[str, str]):
    if not freqs:
        return {"promedio": 0, "varianza": 0, "respuesta": mensajes["e"]}

    prom = sum(freqs) / len(freqs)
    var = sum((x - prom) ** 2 for x in freqs) / len(freqs)

    if var <= 0.2:
        resp = mensajes["e"]
    elif var < 0.6:
        resp = mensajes["f"]
    else:
        resp = mensajes["g"]
    return {"promedio": round(prom, 2), "varianza": round(var, 2), "respuesta": resp}


# ---------------------------------------------------------------------------
#  Sugeridor de sinónimos
# ---------------------------------------------------------------------------

def sugerir_sinonimos(top: Dict[str, int], sinonimos: Dict[str, Dict[str, List[str]]], idioma: str):
    datos_idioma = sinonimos.get(idioma, {})
    sugerencias = []
    for tipo, lista in datos_idioma.items():
        usados = [p for p in lista if p in top]
        restantes = [p for p in lista if p not in usados]
        if usados and restantes:
            sugerencias.append({"tipo": tipo, "usados": usados, "sugerencias": restantes})
    return sugerencias

# ---------------------------------------------------------------------------
#  Analizador principal (idéntico al módulo previo)
# ---------------------------------------------------------------------------

def analizar_texto(texto: str, sinonimos: Dict[str, Dict[str, List[str]]], mensajes: Dict[str, str]):
    total_letras = 0
    palabras: List[str] = []
    total_frases = 0
    palabra_act = ""

    idioma = detectar_idioma(texto, mensajes)

    # Japones ---------------------------------------------------------------
    if idioma == "japones":
        if not texto.endswith("。"):
            texto += "。"
        tagger = Tagger()
        for token in tagger(texto):
            s = token.surface
            if s not in {"。", "、", "!", "?"}:
                palabras.append(s)
                total_letras += len(s)
        total_frases = sum(1 for c in texto if c in "。！？")

    # Alfabéticos -----------------------------------------------------------
    else:
        if not texto.endswith("."):
            texto += "."
        for c in texto:
            if c not in string.whitespace + string.punctuation + "¿¡":
                palabra_act += c.lower()
                total_letras += 1
            else:
                if palabra_act:
                    palabras.append(palabra_act)
                    palabra_act = ""
                if c in ",.;:?!":
                    total_frases += 1
        if palabra_act:
            palabras.append(palabra_act)

    total_palabras = len(palabras)

    # Frecuencias -----------------------------------------------------------
    conteo: Dict[str, int] = {}
    for p in palabras:
        conteo[p] = conteo.get(p, 0) + 1
    ord_frec = dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True))

    top20 = dict(list(ord_frec.items())[:20])
    top5 = dict(list(ord_frec.items())[:5])

    frec_pct = frecuencia_porcentual(top5, total_palabras, mensajes)
    var_info = varianza_poblacional(list(conteo.values()), mensajes)
    moda = palabra_mas_repetida(top5)
    sug = sugerir_sinonimos(top5, sinonimos, idioma)

    return {
        "idioma": idioma,
        "total_palabras": total_palabras,
        "total_letras": total_letras,
        "total_frases": total_frases,
        "palabras_top": top5,
        "palabras_frecuencia": ord_frec,
        "palabras_mas_veces": top20,
        "frecuencias_clasificadas": frec_pct,
        "varianza_info": var_info,
        "palabra_moda": moda,
        "sugerencias_sinonimos": sug,
    }

# ---------------------------------------------------------------------------
#  VISTA PRINCIPAL
# ---------------------------------------------------------------------------

def analizar_texto_view(request: HttpRequest) -> HttpResponse:
    """Vista que muestra un formulario (GET) y procesa el análisis (POST)."""

    contexto: Dict[str, object] = {}

    if request.method == "POST":
        texto = obtener_texto_desde_request(request)
        resultado = analizar_texto(texto, SINONIMOS, DEFAULT_MESSAGES)
        contexto.update({"resultado": resultado, "texto_analizado": texto})

    # Renderiza template – personaliza el nombre según tu estructura
    return render(request, "resultado.html", contexto)