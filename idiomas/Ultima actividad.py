import tkinter as tk
from tkinter import ttk

#Definir la clase película
class Pelicula:
  def __init__(self, nombre: str, pais: str, director: str, genero: str, ano: int, calificacion: float): #Parametrizar el tipo de entrada
    self.__nombre = nombre #privadas
    self.__pais = pais
    self.__director = director
    self.__genero = genero
    self.__ano = ano #tocó así profe jksdhfksu
    self.__calificacion = calificacion

  #get y set de nombre
  def get_nombre(self):
      return self.__nombre
  def set_nombre(self, nombre):
        self.__nombre = nombre

  #get y set de pais
  def get_pais(self):
      return self.__pais
  def set_nombre(self, pais):
        self.__pais = pais

  #get y set de director
  def get_director(self):
      return self.__director
  def set_nombre(self, director):
      self.__director = director

  #get y set de genero
  def get_genero(self):
      return self.__genero
  def set_nombre(self, genero):
      self.__genero = genero

  #get y set de ano
  def get_ano(self):
      return self.__ano
  def set_nombre(self, ano):
      self.__ano = ano

  #get y set de calificacion
  def get_calificacion(self):
      return self.__calificacion
  def set_nombre(self, calificacion):
      self.__calificacion = calificacion

  #Para imprimir la info
  def __str__(self):
        return f"Película: {self.__nombre} del año: ({self.__ano}) - {self.__genero} - Director: {self.__director} - {self.__pais} - IMDb: {self.__calificacion}"

#clase del catálogo
class Catalogo:
  def __init__(self):
        self.__peliculas = [] #la lista del catálogo comienza vacía para kluego ir añadiendole

  def agregar_pelicula(self, pelicula: Pelicula):
      self.__peliculas.append(pelicula) #Se añade el objeto a la lista de peliculas

  def eliminar_pelicula(self, nombre: str):
    nueva_lista = [] #será la lista sin la película que se quiere eliminar
    for pelicula in self.__peliculas:
        if pelicula.get_nombre() != nombre: #Se añaden las películas que no son las que se quiere elimnar
            nueva_lista.append(pelicula)
    self.__peliculas = nueva_lista #resultado: una lista sin esa película

  def mostrar_peliculas(self):
    for pelicula in self.__peliculas: #Mostramos la lista de películas mediante un print
      print(pelicula)


# Interfaz gráfica con ttk
class InterfazPeliculas:
    # Se llama a init para poder crear la ventana principal y ponerle nombre
    def __init__(self, root):
        self.catalogo = Catalogo() #Esta variable almacena las peliculas
        self.root = root
        self.root.title("Catálogo de Películas") #Se pone como nombre Catalogo de peliculas

        # Usar estilo ttk definiendo letras y tamaños
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10, "bold"))

        etiquetas = ["Nombre", "País", "Director", "Género", "Año", "Calificación"]
        self.entradas = {} #Esto va a guardar cada una de las entradas
        #frame para el formulario
        form_frame = ttk.Frame(root, padding="10")
        form_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        etiquetas = ["Nombre", "País", "Director", "Género", "Año", "Calificación"]
        self.entradas = {} #Esto va a guardar cada una de las entradas
        for i, texto in enumerate(etiquetas): #Este bucle ayuda a irlos guardando en formato d lista
            ttk.Label(root, text=texto + ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entrada = ttk.Entry(root, width=40)
            entrada.grid(row=i, column=1, padx=5, pady=5)
            self.entradas[texto.lower()] = entrada
        #Frame para los botones
        botones_frame = ttk.Frame(root, padding="10")
        botones_frame.grid(row=1, column=0, columnspan=2)

        # Estos botones son para las 3 opciones que se necesitaran en nuestro programa
        ttk.Button(root, text="Agregar Película", command=self.agregar_pelicula).grid(row=6, column=0, pady=10)
        ttk.Button(root, text="Eliminar Película", command=self.eliminar_pelicula).grid(row=6, column=1, pady=10)
        ttk.Button(root, text="Mostrar Catálogo", command=self.mostrar_catalogo).grid(row=7, column=0, columnspan=2)

        # Se crea area de texto para que se pueda ver el catalogo
        self.area_texto = tk.Text(root, height=12, width=70)
        self.area_texto.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        # Label de posibles mensajes dependiendo lo que se ponga
        self.mensaje_label = ttk.Label(root, text="", foreground="blue")
        self.mensaje_label.grid(row=9, column=0, columnspan=2, pady=5)

    def mostrar_mensaje(self, texto, color="blue"): #Cambia el color dependiendo lo que salga en la funciòn anterior.
        self.mensaje_label.config(text=texto, foreground=color)

    def agregar_pelicula(self): #Va guardando los valores que se ponen para generar la pelicula
        try:
            nombre = self.entradas["nombre"].get()
            pais = self.entradas["país"].get()
            director = self.entradas["director"].get()
            genero = self.entradas["género"].get()
            ano = int(self.entradas["año"].get())
            calificacion = float(self.entradas["calificación"].get())

            pelicula = Pelicula(nombre, pais, director, genero, ano, calificacion)
            self.catalogo.agregar_pelicula(pelicula)

            self.mostrar_mensaje("Película agregada correctamente.", "green")
            self.limpiar_campos()

        except ValueError:
            self.mostrar_mensaje("Año debe ser entero y calificación decimal.", "red")

    def eliminar_pelicula(self): #Esta funcion busca la pelicula por el nombre y si ya esta, se elimina
        nombre = self.entradas["nombre"].get()
        if nombre:
            self.catalogo.eliminar_pelicula(nombre)
            self.mostrar_mensaje(f"Película '{nombre}' eliminada.", "orange")
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Ingrese el nombre de la película a eliminar.", "red")

    def mostrar_catalogo(self): #Se limpia el area de texto dwspues de que se puestra el catalogo
        self.area_texto.delete("1.0", tk.END)
        peliculas = self.catalogo.mostrar_peliculas()
        if not peliculas:
            self.area_texto.insert(tk.END, "No hay películas registradas.\n")
        else:
            for peli in peliculas:
                self.area_texto.insert(tk.END, str(peli) + "\n")
        self.mostrar_mensaje("Catálogo actualizado.", "blue")

    def limpiar_campos(self): #Borra todos los campos de entrada después de agregar o eliminar una película.
        for entrada in self.entradas.values():
            entrada.delete(0, tk.END)


# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazPeliculas(root)
    root.mainloop()