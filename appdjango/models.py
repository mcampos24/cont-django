from django.db import models

class clientes(models.Model):
    nombre = models.CharField(max_length=100)
    fecha =models.DateTimeField()