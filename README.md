**PARA PODER CORRER JAPONÉS**

Para poder correr desde tu pc el servidor y que funcione el japonés, debes de instalar MeCab, que es el analizador morfológico japonés que fugashi (librería para leer japonés) necesita debajo.

1.  Ve a esta página oficial del instalador:
https://github.com/ikegami-yukino/mecab/releases
2. Descarga el archivo MeCab-0.996.exe (o más reciente).
3. Instálalo (usa los valores por defecto). Asegúrate de anotar la ruta donde se instaló (por defecto es C:\Program Files\MeCab).
4. Abre el Panel de Control → Sistema → Configuración avanzada del sistema → Variables de entorno.
5. Crea una nueva variable de usuario:
  Nombre: MECABRC
  Valor: C:\Program Files\MeCab\etc\mecabrc
  Reinicia tu terminal o VSCode para que tome la variable.
