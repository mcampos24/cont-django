import os
import PyPDF2
from django.conf import settings  #para obtener BASE_DIR

#Django no acepta tkinter porque no es una app de escritorio, entonces cambiamos la manera de obtener el texto
def leer_texto_manual(texto):
    return texto.strip()

def leer_archivo_txt(file_obj):
    return file_obj.read().decode("utf-8")

def leer_pdf(file_obj):
    from PyPDF2 import PdfReader
    texto = ""
    pdf = PdfReader(file_obj)
    for page in pdf.pages:
        texto += page.extract_text()
    return texto

def obtener_texto_desde_request(request):
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

def detectar_idioma(texto, messages=None):
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
        return mensajes["no"]

    return max(puntaje, key=puntaje.get)

import string
from fugashi import Tagger

def analizar_texto(texto):
    total_letras = 0
    palabras = []
    total_frases = 0
    palabra_c = ""

    idioma = detectar_idioma(texto)

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
    frecuencias_top = frecuencia_porcentual(palabras_5_top, total_palabras)
    varianza_info = varianza_poblacional(total_veces, palabras_unicas)
    palabra_moda = palabra_mas_repetida(palabras_5_top)
    sugerencias_sinonimos = sugerir_sinonimos(palabras_5_top, sinonimos, idioma)
    return {
        "idioma": idioma,
        "total_palabras": total_palabras,
        "total_letras": total_letras,
        "total_frases": total_frases,
        "palabras_top": palabras_top,
        "palabras_frecuencia": palabra_veces_ord,
        "palabras_mas_veces": palabras_mas_veces,
        "frecuencias_clasificadas": frecuencias_top,
        "varianza_info": varianza_info,
        "palabra_moda": palabra_moda,
        "sugerencias_sinonimos": sugerir_sinonimos,
    }
def palabra_mas_repetida(palabras_5_top):
    return {list(palabras_5_top.keys())[0]}

def frecuencia_porcentual(palabras_5_top, total_palabras, mensajes =None):

    resultado = {}

    for palabra in palabras_5_top:
        frecuencia_porcentual = round(palabras_5_top[palabra] / total_palabras * 100, 2) #Porcentaje de cada palabra en el textos
        if frecuencia_porcentual >= 30:
            respuesta = f"{palabra} {mensajes.get('y')} {frecuencia_porcentual} % {mensajes.get('z')}"
        elif frecuencia_porcentual >= 15:
            respuesta = f"{palabra} {mensajes.get('y')} {frecuencia_porcentual} % {mensajes.get('a')}"
        elif frecuencia_porcentual < 15 and frecuencia_porcentual >= 5:
            respuesta = f"{palabra} {mensajes.get('y')} {frecuencia_porcentual} % {mensajes.get('b')}"
        else:
            respuesta = f"{palabra} {mensajes.get('y')} {frecuencia_porcentual} % {mensajes.get('d')}"

        resultado[palabra] = respuesta
    return resultado

def varianza_poblacional(total_veces, palabras_unicas, mensajes= None):
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
        respuesta = mensajes.get(e)
    elif 0.2 < varianza < 0.6:
        respuesta = mensajes.get(f)
    else:
        respuesta = mensajes.get(g)

    return {
        "promedio": round(promedio, 2),
        "varianza": round(varianza, 2),
        "respuesta": respuesta
    }
def sugerir_sinonimos(palabras_5_top, sinonimos, id_sinonimos):
    idioma_de_sinonimos = sinonimos[id_sinonimos]  
    sugerencias = []

    for tipo_palabra, listas in idioma_de_sinonimos.items():
        usados = []  

        for palabra in listas:
            if palabra in palabras_5_top:
                usados.append(palabra)

        if len(usados) > 0:
            sugerencias_tipo = []  
            for palabra in listas:
                if palabra not in usados:
                    sugerencias_tipo.append(palabra)

            if len(sugerencias_tipo) > 0:
                sugerencias.append({
                    "tipo": tipo_palabra,
                    "usados": usados,
                    "sugerencias": sugerencias_tipo
                    })
    return sugerencias 