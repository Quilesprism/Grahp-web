
from django.db import models



class Movimiento(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    registro = models.BigIntegerField()
    uid = models.CharField(max_length=200)  
    intento = models.IntegerField() 
    movimiento = models.IntegerField()  
    trayectoria = models.CharField(max_length=50)  

    def __str__(self):
        return f"Movimiento {self.movimiento} en intento {self.intento} para registro {self.registro}"
