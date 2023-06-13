from django.contrib import admin

from carWash.models import Cate_ser, Contrato_ser, Estado, Servicios, Vehiculo

# Register your models here.
admin.site.register(Cate_ser)
admin.site.register(Servicios)
admin.site.register(Contrato_ser)
admin.site.register(Vehiculo)
admin.site.register(Estado)