import os
from django.conf import settings  #para obtener BASE_DIR
from .idiomas import mensajes_por_idioma
from django.http import HttpRequest, HttpResponse

#Django no acepta tkinter porque no es una app de escritorio, entonces cambiamos la manera de obtener el texto
def leer_texto_manual(texto: str):
    return texto.strip()

def leer_archivo_txt(file_obj):
    return file_obj.read().decode("utf-8", errors="ignore")

def leer_pdf(file_obj):
    from PyPDF2 import PdfReader
    texto = ""
    pdf = PdfReader(file_obj)
    for page in pdf.pages:
        texto += page.extract_text() or ""
    return texto

def obtener_texto_desde_request(request: HttpRequest):
    modo = request.POST.get("modo")
    if modo == "escribir":
        return leer_texto_manual(request.POST.get("texto", ""))
    elif modo == "archivo":
        archivo = request.FILES.get("archivo")
        if archivo:
            if archivo.name.endswith(".txt"):
                return leer_archivo_txt(archivo)
            elif archivo.name.endswith(".pdf"):
                return leer_pdf(archivo)
    return ""

def detectar_idioma(texto, mensajes):
    texto = texto.lower()

    archivos_idioma = {
        "español": "español.txt",
        "portugues": "portugues.txt",
        "japones": "japones.txt",
        "ingles": "ingles.txt",
    }

    puntaje = {idioma: 0 for idioma in archivos_idioma}

    for idioma, archivo in archivos_idioma.items():
        ruta = os.path.join(settings.BASE_DIR, 'idiomas', archivo)
        if not os.path.exists(ruta):
            continue  #evita error si el archivo no existe
        with open(ruta, "r", encoding="utf-8") as f:
            contenido = f.read().lower().replace("\n", " ")
            palabras = contenido.split()
        for palabra in palabras:
            if palabra in texto:
                puntaje[idioma] += texto.count(palabra)

    if all(p == 0 for p in puntaje.values()):
        return mensajes.get('no')

    return max(puntaje, key=puntaje.get)

# Cargar los 4 diccionarios creados
csv_esp = os.path.join(settings.BASE_DIR,  "idiomas", "español.csv")
csv_ing = os.path.join(settings.BASE_DIR,  "idiomas", "ingles.csv")
csv_por = os.path.join(settings.BASE_DIR, "idiomas", "portugues.csv")
csv_jap = os.path.join(settings.BASE_DIR,  "idiomas", "japones.csv") 

def cargar_diccionario(ruta_csv):
    diccionario = {}
    with open(ruta_csv, "r", encoding="utf-8") as archivo:
        lineas = archivo.readlines()

    for linea in lineas[1:]:
        partes = linea.strip().split(",")
        if len(partes) < 2:
            continue
        grupo = partes[0].strip()
        palabras = [p.strip() for p in partes[1:] if p.strip()]
        diccionario[grupo] = palabras

    return diccionario

# Diccionarios por idioma
diccionarios = {
    "español": cargar_diccionario(csv_esp),
    "ingles": cargar_diccionario(csv_ing),
    "portugues": cargar_diccionario(csv_por),
    "japones": cargar_diccionario(csv_jap)
}

# Esta función busca la palabra en el idioma del texto
def sugerir_sinonimos(palabras_10_top, idioma):
    sugerencias = []
    dic = diccionarios.get(idioma, {})

    for palabra in palabras_10_top:
        palabra_buscar = palabra.lower().strip()
        encontrado = False

        for grupo, lista in dic.items():
            lista_min = [p.lower() for p in lista]
            if palabra_buscar in lista_min:
                sinonimos = [p for p in lista if p.lower() != palabra_buscar]
                if sinonimos:
                    sugerencias.append({
                        "palabra": palabra,
                        "grupo": grupo,
                        "sinonimos": sinonimos
                    })
                encontrado = True
                break
        
        if not encontrado:
            sugerencias.append({
                "palabra": palabra,
                "grupo": None,
                "sinonimos": []
            })

    return sugerencias

import string
from fugashi import Tagger

def analizar_texto(texto: str, mensajes):
    total_letras = 0
    palabras = []
    total_frases = 0
    palabra_c = ""

    idioma = detectar_idioma(texto, mensajes)

    if idioma == "japones":
        if not texto.endswith("。"):
            texto += "。"
        tagger = Tagger()
        for token in tagger(texto):
            palabra = token.surface
            if palabra not in {"。", "、", "!", "?"}:
                palabras.append(palabra)
                total_letras += len(palabra)
        for c in texto:
            if c in "。！？、":
                total_frases += 1

    else:
        if not texto.endswith("."):
            texto += "."
        for c in texto:
            if c != " " and c not in string.punctuation + "¿¡":
                palabra_c += c
                total_letras += 1
            elif palabra_c != "" and c == " ":
                palabras.append(palabra_c.lower())
                palabra_c = ""
            elif c in ",.;:?!":
                total_frases += 1
            elif c in string.punctuation + "¿¡":
                continue
        if palabra_c != "":
            palabras.append(palabra_c.lower())

    total_palabras = len(palabras)

    palabras_unicas = []
    total_veces = []
    for palabra in palabras:
        if palabra not in palabras_unicas:
            palabras_unicas.append(palabra)
            veces = palabras.count(palabra)
            total_veces.append(veces)

    palabra_veces = {palabra: palabras.count(palabra) for palabra in palabras_unicas}
    palabra_veces_ord = dict(sorted(palabra_veces.items(), key=lambda x: x[1], reverse=True))
    palabras_mas_veces = dict(list(palabra_veces_ord.items())[:20])
    palabras_5_top = dict(list(palabra_veces_ord.items())[:5])
    palabras_10_top = dict(list(palabra_veces_ord.items())[:10])
    frecuencias_top = frecuencia_porcentual(palabras_10_top, total_palabras, mensajes)
    varianza_info = varianza_poblacional(total_veces, palabras_unicas, mensajes)
    palabra_moda = palabra_mas_repetida(palabras_5_top)
    sugerencias = sugerir_sinonimos(palabras_5_top, idioma)
    return {
        "idioma": idioma,
        "total_palabras": total_palabras,
        "total_letras": total_letras,
        "total_frases": total_frases,
        "palabras_top": palabras_10_top,
        "palabras_frecuencia": palabra_veces_ord,
        "palabras_mas_veces": palabras_mas_veces,
        "frecuencias_clasificadas": frecuencias_top,
        "varianza_info": varianza_info,
        "palabra_moda": palabra_moda,
        "sugerencias_sinonimos": sugerencias,
    }
def palabra_mas_repetida(palabras_5_top):
    return next(iter(palabras_5_top))

def frecuencia_porcentual(palabras_10_top, total_palabras, mensajes):
    resultado = {}

    for palabra in palabras_10_top:
        frecuencia = round(palabras_10_top[palabra] / total_palabras * 100, 2)

        if frecuencia >= 30:
            comentario = mensajes.get('z')
        elif frecuencia >= 15:
            comentario = mensajes.get('a')
        elif frecuencia >= 5:
            comentario = mensajes.get('b')
        else:
            comentario = mensajes.get('d')

        resultado[palabra] = {
            "porcentaje": frecuencia,
            "comentario": f"{palabra} {mensajes.get('y')} {frecuencia}% {comentario}"
        }

    return resultado

def varianza_poblacional(total_veces, palabras_unicas, mensajes):
    #Cálculo de promedio de frecuencia.
    suma_frecuencias = 0
    for i in total_veces:
        suma_frecuencias += i
        promedio = suma_frecuencias / len(palabras_unicas)
    #Cálculo de varianza poblacional de frecuencia.
    nu = 0
    for i in total_veces:
        nu += (i - promedio)**2
        varianza = nu / len(palabras_unicas)
    #Dependiendo de la varianza que tenga el texto
    if varianza <= 0.2:
        respuesta = mensajes.get('e')
    elif 0.2 < varianza < 0.6:
        respuesta = mensajes.get('f')
    else:
        respuesta = mensajes.get('g')

    return {
        "promedio": round(promedio, 2),
        "varianza": round(varianza, 2),
        "respuesta": respuesta
    }
