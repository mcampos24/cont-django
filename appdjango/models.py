from django.db import models

#este archivo es prácticamente el que permite el acceso al cliente a la pg
class clientes(models.Model):
    nombre = models.CharField(max_length=100) #para ver la actividad del usuario 
    fecha =models.DateTimeField() #la fecha y hora en la que la ejecutó