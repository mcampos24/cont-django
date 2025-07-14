import tkinter as tk
from tkinter import ttk

# Clase Película
class Pelicula:
    def __init__(self, nombre, pais, director, genero, ano, calificacion):
        self.__nombre = nombre
        self.__pais = pais
        self.__director = director
        self.__genero = genero
        self.__ano = ano
        self.__calificacion = calificacion

    def get_nombre(self): return self.__nombre
    def set_nombre(self, nombre): self.__nombre = nombre

    def get_pais(self): return self.__pais
    def set_pais(self, pais): self.__pais = pais

    def get_director(self): return self.__director
    def set_director(self, director): self.__director = director

    def get_genero(self): return self.__genero
    def set_genero(self, genero): self.__genero = genero

    def get_ano(self): return self.__ano
    def set_ano(self, ano): self.__ano = ano

    def get_calificacion(self): return self.__calificacion
    def set_calificacion(self, calificacion): self.__calificacion = calificacion

    def __str__(self):
        return f"Película: {self.__nombre} ({self.__ano}) - {self.__genero} - Director: {self.__director} - {self.__pais} - IMDb: {self.__calificacion}"


# Clase Catálogo
class Catalogo:
    def __init__(self):
        self.__peliculas = []

    def agregar_pelicula(self, pelicula: Pelicula):
        self.__peliculas.append(pelicula)

    def eliminar_pelicula(self, nombre: str):
        self.__peliculas = [p for p in self.__peliculas if p.get_nombre() != nombre]

    def obtener_peliculas(self):
        return self.__peliculas


# Interfaz gráfica con ttk
class InterfazPeliculas:
    def __init__(self, root):
        self.catalogo = Catalogo()
        self.root = root
        self.root.title("Catálogo de Películas")

        # Usar estilo ttk
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("TButton", font=("Arial", 10, "bold"))

        etiquetas = ["Nombre", "País", "Director", "Género", "Año", "Calificación"]
        self.entradas = {}

        for i, texto in enumerate(etiquetas):
            ttk.Label(root, text=texto + ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entrada = ttk.Entry(root, width=40)
            entrada.grid(row=i, column=1, padx=5, pady=5)
            self.entradas[texto.lower()] = entrada

        # Botones
        ttk.Button(root, text="Agregar Película", command=self.agregar_pelicula).grid(row=6, column=0, pady=10)
        ttk.Button(root, text="Eliminar Película", command=self.eliminar_pelicula).grid(row=6, column=1, pady=10)
        ttk.Button(root, text="Mostrar Catálogo", command=self.mostrar_catalogo).grid(row=7, column=0, columnspan=2)

        # Área de texto
        self.area_texto = tk.Text(root, height=12, width=70)
        self.area_texto.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        # Label de mensaje (reemplaza messagebox)
        self.mensaje_label = ttk.Label(root, text="", foreground="blue")
        self.mensaje_label.grid(row=9, column=0, columnspan=2, pady=5)

    def mostrar_mensaje(self, texto, color="blue"):
        self.mensaje_label.config(text=texto, foreground=color)

    def agregar_pelicula(self):
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

    def eliminar_pelicula(self):
        nombre = self.entradas["nombre"].get()
        if nombre:
            self.catalogo.eliminar_pelicula(nombre)
            self.mostrar_mensaje(f"Película '{nombre}' eliminada.", "orange")
            self.limpiar_campos()
        else:
            self.mostrar_mensaje("Ingrese el nombre de la película a eliminar.", "red")

    def mostrar_catalogo(self):
        self.area_texto.delete("1.0", tk.END)
        peliculas = self.catalogo.obtener_peliculas()
        if not peliculas:
            self.area_texto.insert(tk.END, "No hay películas registradas.\n")
        else:
            for peli in peliculas:
                self.area_texto.insert(tk.END, str(peli) + "\n")
        self.mostrar_mensaje("Catálogo actualizado.", "blue")

    def limpiar_campos(self):
        for entrada in self.entradas.values():
            entrada.delete(0, tk.END)


# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazPeliculas(root)
    root.mainloop()