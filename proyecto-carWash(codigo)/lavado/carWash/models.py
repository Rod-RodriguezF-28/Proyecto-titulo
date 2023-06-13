from django.db import models

# Create your models here.
class Cate_ser(models.Model):
    id_cate = models.AutoField(primary_key=True)
    tipo_ser = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.tipo_ser

class Servicios(models.Model):
    id_ser = models.AutoField(primary_key=True)
    nombre_ser = models.CharField(max_length=50, blank=True, null=True)
    precio_ser = models.IntegerField()
    categoria_ser = models.ForeignKey(Cate_ser, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nombre_ser


class Vehiculo(models.Model):
    id_vehi = models.AutoField(primary_key=True)
    cate_vehi = models.CharField(max_length=20)
    
    def __str__(self):
        return self.cate_vehi

class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    estado_ser = models.CharField(max_length=50)
    
    def __str__(self):
        return self.estado_ser

class Contrato_ser(models.Model):
    id_contrato = models.AutoField(primary_key=True)
    fecha_ini = models.DateField()
    dueno = models.CharField(max_length=45, default='--')
    vehi = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    estado_es = models.ForeignKey(Estado, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.dueno