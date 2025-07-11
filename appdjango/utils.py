import os, re
from django.conf import settings  #para obtener BASE_DIR
from .idiomas import mensajes_por_idioma
from django.http import HttpRequest
from fugashi import Tagger

#Django no acepta tkinter porque no es una app de escritorio, entonces cambiamos la manera de obtener el texto
def leer_texto_manual(texto: str):
    return texto.strip() #si es un texto normal tipo str simplemente lo dividimos

def leer_archivo_txt(file_obj):
    return file_obj.read().decode("utf-8", errors="ignore") #si es un archivo txt lo leemos en utf-8 y si existe algún error, lo ignoramos

def leer_pdf(file_obj): #para leer el pdf usamos las librerías correspondientes
    from PyPDF2 import PdfReader 
    texto = "" #comienza vacío
    pdf = PdfReader(file_obj) #usamos la función de la librería
    for page in pdf.pages: #por cada página vamos extrayengo el texto para finalmente retornarlo completo
        texto += page.extract_text() or ""
    return texto #retornamos el texto acomulado

#para el formulario donde se envía el texto
def obtener_texto_desde_request(request: HttpRequest): #ir a views para visualizar request
    modo = request.POST.get("modo") #dependiendo de la selección se determinada el modo en el que el usuario va a subir las cosas
    if modo == "escribir":
        return leer_texto_manual(request.POST.get("texto", "")) #si solo es un str, llamamos a leer_texto_manual respecto al texto enviado
    elif modo == "archivo":
        archivo = request.FILES.get("archivo") #si solo es un archivo, llamamos las funciones dependiendo de si es txt o pdf
        if archivo:
            if archivo.name.endswith(".txt"): #si es txt
                return leer_archivo_txt(archivo) #llamamos a la función para leet archivos txt 
            elif archivo.name.endswith(".pdf"): #si es pdf
                try: #por si hay algún error, lo metemos en un try
                    return leer_pdf(archivo) #llamamos a la función para leer archivos pdf
                except Exception as e: #cualquier error que ocurra 
                    return "Error"
    return "" #Si no se detecta ningún texto válido o el modo no está definido, se retorna una cadena vacía

# En estos apartados se hace la adaptación al cuaderno de colab para una mayor organización en funciones.
#Pre-inicializa el tagger de japonés
TAGGER = Tagger()

def detectar_idioma(texto: str, mensajes: dict): #daba un montón de errores entonces aquí por si algo se le condiciona a ser string
    texto = texto.strip()
    #tokenizamos:
    if re.search(r'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF]', texto): #el re permite la búsqueda de esos carácteres
        #Contiene caracteres japoneses usando fugashi
        tokens = [t.surface for t in TAGGER(texto)] #Los "tokens superficiales" son las palabras tal como aparecen, en analizar texto se ve prácticamente esta misma línea, solo que con otras variables.
    else:
        #extraemos palabras latinas completas, (si no es japonés, extraemos palabras normales (letras, números, etc.))
        tokens = re.findall(r'\b\w+\b', texto.lower()) #nuevamente un re para buscar, todo esto en la cadena en minúsculas

    archivos = {
        #Diccionario que asocia cada idioma con su archivo .txt de palabras mas usadas
        "español": "español.txt",
        "portugues": "portugues.txt",
        "ingles":  "ingles.txt",
        "japones": "japones.txt",
    }
    puntaje = {} #aquí se registrapan los puntajes por idioma
    for idioma, archivo in archivos.items(): #por los archivos de texto
        #Se abre y lee el archivo con palabras clave del idioma (usando "utf-8" como codificación)
        path = os.path.join(settings.BASE_DIR, "idiomas", archivo)
        if not os.path.exists(path):
            puntaje[idioma] = 0 #el puntaje de los idiomas será 0 para evitar error si el archivo no existe
            continue 
        palabras_clave = open(path, encoding="utf-8").read().lower().split()
        #contamos cuántas palabras del texto están en las palabras clave
        contador = sum(1 for w in tokens if w.lower() in palabras_clave)
        puntaje[idioma] = contador #cuántas por cada idioma

     #Si ningún idioma obtuvo puntaje (0 coincidencias en todos), no se detectó idioma
    if all(p == 0 for p in puntaje.values()):
        return mensajes.get("no", "Idioma no detectado")
    #Se retorna el idioma con el puntaje más alto (el más probable), si hay empate, max() escoge el primero en orden dict
    return max(puntaje, key=puntaje.get)

# Cargar los 4 diccionarios creados
csv_esp = os.path.join(settings.BASE_DIR,  "idiomas", "español.csv")
csv_ing = os.path.join(settings.BASE_DIR,  "idiomas", "ingles.csv")
csv_por = os.path.join(settings.BASE_DIR, "idiomas", "portugues.csv")
csv_jap = os.path.join(settings.BASE_DIR,  "idiomas", "japones.csv") 

#carga los csv para los sinonimos
def cargar_diccionario(ruta_csv):
    diccionario = {} #guarda los valores
    with open(ruta_csv, "r", encoding="utf-8") as archivo: #abrimos el archivo para leer y lo decodificamos con utf-8
        lineas = archivo.readlines() #leer las lineas

    #Recorre las líneas desde la segunda (omite la primera fila)
    for linea in lineas[1:]:
        partes = linea.strip().split(",") #Elimina espacios y divide la línea por comas
        if len(partes) < 2: #Si la línea no tiene al menos un grupo y una palabra, la salta
            continue
        grupo = partes[0].strip() #grupo corresponde a la primera columna
        palabras = [p.strip() for p in partes[1:] if p.strip()] #palabras son 
        diccionario[grupo] = palabras #Se asignan las palabras al grupo en el diccionario

    return diccionario #Devuelve el diccionario completo

# Diccionarios por idioma
diccionarios = {
    "español": cargar_diccionario(csv_esp),
    "ingles": cargar_diccionario(csv_ing),
    "portugues": cargar_diccionario(csv_por),
    "japones": cargar_diccionario(csv_jap)
}

# Esta función busca la palabra en el idioma del texto
def sugerir_sinonimos(palabras_10_top, idioma):
    sugerencias = [] #lista para almacenar los resultados (sugerencias de sinónimos)
    dic = diccionarios.get(idioma, {}) #Obtiene el diccionario correspondiente al idioma; si no existe, devuelve {}

    #Itera sobre cada palabra de las más frecuentes
    for palabra in palabras_10_top:
        palabra_buscar = palabra.lower().strip() # texto limpio: minúsculas y sin espacios
        encontrado = False #Saber si la palabra fue encontrada

        #Recorre cada grupo de sinónimos dentro del diccionario del idioma
        for grupo, lista in dic.items():
            lista_min = [p.lower() for p in lista] #limpia todas las palabras del grupo
            if palabra_buscar in lista_min:  #Si la palabra aparece en el grupo
                sinonimos = [p for p in lista if p.lower() != palabra_buscar] #Excluye la palabra original de los sinónimos sugeridos
                if sinonimos: #Si hay sinónimos que sugerir
                    sugerencias.append({ #Agrega una sugerencia con la palabra, su grupo y sus sinónimos
                        "palabra": palabra,
                        "grupo": grupo,
                        "sinonimos": sinonimos
                    })
                encontrado = True #Marca que ya se encontró la palabra
                break
        
        if not encontrado: #Si no se encontró la palabra en ningún grupo, aún se agrega como resultado sin sinónimos
            sugerencias.append({
                "palabra": palabra,
                "grupo": None,
                "sinonimos": []
            })

    return sugerencias #Devuelve la lista de sugerencias generadas

import string

#Limpieza de cadena y contador de letras, frases y palabras (Esta es la función principal a la que los views recurren, por eso su return es un diccionario con los resultados de las demás funciones)
def analizar_texto(texto: str, mensajes):
    total_letras = 0 #Contador de letras
    palabras = [] #Lista de todas las palabras del texto
    total_frases = 0 #Contador de frases
    palabra_c = ""

    idioma = detectar_idioma(texto, mensajes)

    #para japonés
    if idioma == "japones": 
        if not texto.endswith("。"): #Por si el usuario no pone un punto al final, para que el programa cuente la última frase
            texto += "。"
        tagger = Tagger()  #Crea un analizador morfológico japonés
        for token in tagger(texto):
            palabra = token.surface #Superficie: palabra tal como aparece
            if palabra not in {"。", "、", "!", "?"}:
                palabras.append(palabra)
                total_letras += len(palabra) #Cada carácter se considera "letter"
        for c in texto:
            if c in "。！？、":
                total_frases += 1 #Conteo de frases basado en signos de puntuación japonesa
    #Para Español, Inglés y portugués
    else:
        if not texto.endswith("."): #Por si el usuario no pone un punto al final, para que el programa cuente la última frase
            texto += "."
        for c in texto:
            if c != " " and c not in string.punctuation + "¿¡":  #Cuando sea una letra
                palabra_c += c #Va acomulando las letras hasta el espacio, guardando palabras.
                total_letras += 1  #Suma de letras
            elif palabra_c != "" and c == " ": #Cuando se encuentra con un espacio.
                palabras.append(palabra_c.lower()) #Añade a la lista "palabas"
                palabra_c = "" #Se reinicia la variable que acomula las letras, para empezar otra palabra
            elif c in ",.;:?!": #Cuando encuentre un signo de puntuación
                total_frases += 1  #Se suma a las frases
            elif c in string.punctuation + "¿¡": #Si es un signo de puntuación se omitirá.
                continue
        if palabra_c != "": #Esto añade la última palabra del texto
            palabras.append(palabra_c.lower())
    #Contador de palabras
    total_palabras = len(palabras) #Cuenta la cantidad de elementos en la lista de palabras.

    palabras_unicas = [] #Lista que guarda los valores
    total_veces = [] #Lista de palabras únicas
    for palabra in palabras: #palabra recorre la lista de palabras
        if palabra not in palabras_unicas: #Si ya fue contada la palabra, entonces no se vuelve a contar
            palabras_unicas.append(palabra)
            veces = palabras.count(palabra) #Se calcula las veces que aparece cada palabra
            total_veces.append(veces) #Anexa a la lista

    #Llama a las demás funciones que se requieran
    palabra_veces = {palabra: palabras.count(palabra) for palabra in palabras_unicas} #diccionario con las veces de repeticion
    palabra_veces_ord = dict(sorted(palabra_veces.items(), key=lambda x: x[1], reverse=True)) #diccionario de las palabras ordenadas por cantidad de veces, gracias al diccionario anterior
    palabras_5_top = dict(list(palabra_veces_ord.items())[:5]) #diccionario para la moda
    palabras_10_top = dict(list(palabra_veces_ord.items())[:10]) #para la gráfica de barras
    frecuencias_top = frecuencia_porcentual(palabras_10_top, total_palabras, mensajes) #Para la tabla con frecuencias
    varianza_info = varianza_poblacional(total_veces, palabras_unicas, mensajes)
    palabra_moda = palabra_mas_repetida(palabras_5_top) #palabra moda
    sugerencias = sugerir_sinonimos(palabras_5_top, idioma) #para los sinonimos
    return { #aquí retornamos el diccionario con las claves a las que se recurrirá para acceder a los valores en el html
        "idioma": idioma, 
        "total_palabras": total_palabras,
        "total_letras": total_letras,
        "total_frases": total_frases,
        "palabras_top": palabras_10_top,
        "palabras_frecuencia": palabra_veces_ord,
        "frecuencias_clasificadas": frecuencias_top,
        "varianza_info": varianza_info,
        "frecuencia_todas": palabra_veces,
        "palabra_moda": palabra_moda,
        "sugerencias_sinonimos": sugerencias,
    }
def palabra_mas_repetida(palabras_5_top):
    if not palabras_5_top: #Si no se encuentra nada (prevenir errores)
        return ""

    max_veces = max(palabras_5_top.values()) #oraniza a las palabras más repetidas
    palabras_max = [p for p, v in palabras_5_top.items() if v == max_veces] #es para que imprima las más repetidas y que tenga en cuenta si 2 o más se repiten la misma cantidad
    return ", ".join(palabras_max) #se separan por comas si es que hay más de una, sino, pues sólo es la palabra única.

def frecuencia_porcentual(palabras_10_top, total_palabras, mensajes):
    resultado = {}

    for palabra in palabras_10_top:
        frecuencia = round(palabras_10_top[palabra] / total_palabras * 100, 2) #Porcentaje de cada palabra en el textos

        if frecuencia >= 15: #dependiendo de qué tando se repiten mandamos un mensaje de sugerencia
            comentario = mensajes.get('z')
        elif frecuencia >= 10:
            comentario = mensajes.get('a')
        elif frecuencia >= 5:
            comentario = mensajes.get('b')
        else:
            comentario = mensajes.get('d') #comentarios dependientes del switch del idioma

        #para poder mostrar los resultados los guardamos en un diccionario.
        resultado[palabra] = {
            "porcentaje": frecuencia,
            "comentario": f"{palabra} {mensajes.get('y')} {frecuencia}% {comentario}"
        }

    return resultado #retornamos el diccionario

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
    if varianza <= 1:
        respuesta = mensajes.get('e')
    elif 1 < varianza <= 4:
        respuesta = mensajes.get('f')
    else:
        respuesta = mensajes.get('g')

    return {
        "promedio": round(promedio, 2),
        "varianza": round(varianza, 2),
        "respuesta": respuesta
    }



from wordcloud import WordCloud
def generar_nube_palabras(texto): #la nube se genera a partir del texto limpio
    
    ruta_directorio = "static/img"
    os.makedirs(ruta_directorio, exist_ok=True)

    #Crear la nube 
    nube = WordCloud(
        width=800,
        height=400,
        background_color="#f9f5f0", #fondo de la misma pg
        colormap="plasma",
        font_path="static/fuente/notosans.ttf",  #se añade una fuente que soporta los carácteres japoneses
        max_words=100,
    ).generate(texto)

    #Guardar la imagen
    nube.to_file("static/img/nube.png") #posteriormente en views, se muestra (ver views y html)
