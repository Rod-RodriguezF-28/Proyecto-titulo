from django.shortcuts import render
from django.db import connection
import cx_Oracle

# importar el modelo de tabla de usuario desde el administrador
from django.contrib.auth.models import User
# importar una libreria de autentificacion 
from django.contrib.auth import authenticate, logout, login
# importar libreria decoradora que evita el ingreso a las paginas sin autorizacion 
from django.contrib.auth.decorators import login_required, permission_required

from carWash.models import Cate_ser, Contrato_ser, Estado, Servicios, Vehiculo
from django.contrib import messages
from django.http import HttpResponse
import csv
from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter


# Create your views here.



#---------------------------------------------------------------

def index(request):
    return render(request, "index.html")

#---------------------------------------------------------------

def registrar(request):
    mensaje = ""
    if request.POST:
        correo_user = request.POST.get("email")
        usuario = request.POST.get("usuario")
        nombre_user = request.POST.get("nombre")
        apellido_user = request.POST.get("apeliido")
        pass_user = request.POST.get("txtPass1")
        
        try:
            usu = User.objects.get(username = usuario)
            mensaje = "usuario ya existe"
        except:
            usu = User()
            usu.username = usuario
            usu.first_name = nombre_user
            usu.last_name = apellido_user
            usu.email = correo_user
            usu.set_password(pass_user)
            usu.save()
            mensaje = "Usuario registrado con exito"
    contexto = {"mensaje":mensaje}
    return render(request, "registrarse.html", contexto)

#---------------------------------------------------------------

def cerrar_sesion(request):
    logout(request)
    return render(request, "iniciarSesion.html")

#---------------------------------------------------------------

def iniciar(request):
    mensaje = ""
    if request.POST:
        usuario = request.POST.get("usuario")
        contra = request.POST.get("pass1")
        us = authenticate(request, username=usuario, password=contra)
        if us is not None and us.is_active:
            login(request, us)
            return render(request, "index.html")
        else:
            mensaje = "usuario o contraseña incorrectos"
    contexto = {"mensaje":mensaje}
    return render(request, "iniciarSesion.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
def servicios(request):
    contexto = {
        "servicios":listado_servicios()
    }
    return render(request, "servicios.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
def info_ser(request, id):
    estado  = listado_estado_def() 
    servicio = Servicios.objects.get(nombre_ser=id)
    contexto = {"servicio":servicio, "vehiculos":listado_vehiculo(), "estado":estado}
    return render(request, "info_contrato.html", contexto)


#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
def insertar_contrato(request):
    usuario_actual = request.user.username
    contexto = {
        "categorias":listado_categorias()
    }
    if request.POST:
        nom_servicio = request.POST.get("nombre_servicio")
        fecha_ini = request.POST.get("fecha_ini")
        cate_vhi = request.POST.get("cate_vehi")
        dueno = usuario_actual
        estado_ser = request.POST.get("estado")
        salida = agregar_contrato(fecha_ini , dueno, estado_ser, nom_servicio, cate_vhi)
        if salida == 1:
            contexto["mensaje"] = "Servicio agregado"
        else:
            contexto["mensaje"] = "Error al agregar el servicio"
    return render(request, "info_contrato.html", contexto)
#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def agregar_ser(request):
    contexto = {
        "servicios":listado_servicios()
    }
    return render(request, "agregar_servicios.html", contexto)

#---------------------------------------------------------------
@login_required(login_url='/iniciar/')
def agenda_cli(request):
    contratos  = Contrato_ser.objects.filter(dueno = request.user.username) 
    contexto = {"contratos":contratos}
    return render(request, "agenda_cli.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
def cancelar_contrato(request, id):
    mensaje = ""
    try:
        con = Contrato_ser.objects.get(id_contrato = id)
        con.delete()
        mensaje = "Contrato cancelado"
        
    except:
        mensaje = "Error al cancelar el contrato"
    contratos  = Contrato_ser.objects.filter(dueno = request.user.username) 
    contexto = {"contratos":contratos, "mensaje":mensaje}
    return render(request, "agenda_cli.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
def cancelar_contr_cli(request, id):
    mensaje = ""
    try:
        con = Contrato_ser.objects.get(id_contrato = id)
        con.delete()
        mensaje = "Contrato cancelado"
        
    except:
        mensaje = "Error al cancelar el contrato"
    contratos  = listado_contratos()
    contexto = {"contratos":contratos, "mensaje":mensaje}
    return render(request, "agenda_admin.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def agenda_ad(request):
    contexto = {
        "contratos":listado_contratos()
    }
    return render(request, "agenda_admin.html", contexto)

#---------------------------------------------------------------
#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def export_pdf(request):
    contexto = {
        "contratos":listado_contratos(),
        "cantidad":contratos(),
        "completos":contratos_completos()
    }
    return render(request, "export_pdf.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def form_agre_ser(request):
    contexto = {
        "categorias":listado_categorias()
    }
    if request.POST:
        nombre_ser = request.POST.get("nombre_servicio")
        precio_ser = request.POST.get("precio_servicio")
        categoria_ser_id = request.POST.get("categoria")
        salida = agregar_servicio(nombre_ser, precio_ser, categoria_ser_id)
        if salida == 1:
            contexto["mensaje"] = "Servicio agregado"
        else:
            contexto["mensaje"] = "Error al agregar el servicio"
        
    return render(request, "form_agre_serv.html", contexto)


#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def form_agre_cate(request):
    contexto = {
        "categorias":listado_categorias()
    }
    if request.POST:
        tipo_ser = request.POST.get("tipo_ser")
        salida = agregar_categoria(tipo_ser)
        if salida == 1:
            contexto["mensaje"] = "Categoria agregada"
        else:
            contexto["mensaje"] = "Error al agregar la categoria"
    return render(request, "form_agre_cate.html", contexto)
    

#---------------------------------------------------------------
@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def cate_esta(request):
    contexto = {"categorias":listado_categorias()}
    return render(request, "cate_esta.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.delete_servicios', login_url='/iniciar/')
def eliminar_cate(request, id):
    mensaje = ""
    try:
        cat = Cate_ser.objects.get(tipo_ser = id)
        cat.delete()
        mensaje = "Categoria eliminada"
    except:
        mensaje = "Error al eliminar la categoria"

    contexto = {
        "categorias":listado_categorias(), "mensaje":mensaje
    }
    return render(request, "cate_esta.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def estado(request):
    contexto = {"estados":listado_estado()}
    return render(request, "estado.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def form_agre_esta(request):
    contexto = {
        "estados":listado_estado()
    }
    if request.POST:
        estado_ser = request.POST.get("estado_ser")
        salida = agregar_estado(estado_ser)
        if salida == 1:
            contexto["mensaje"] = "Estado agregado"
        else:
            contexto["mensaje"] = "Error al agregar el estado"
    return render(request, "form_agre_esta.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def form_agre_auto(request):
    contexto = {
        "vehiculos":listado_vehiculo()
    }
    if request.POST:
        cate_vehi = request.POST.get("cate_vehi")
        salida = agregar_vehiculo(cate_vehi)
        if salida == 1:
            contexto["mensaje"] = "Categoria de vehiculo agregada"
        else:
            contexto["mensaje"] = "Error al agregar la categoria del vehiculo"
    return render(request, "form_agre_auto.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.add_servicios',login_url='/iniciar/')
def vehi(request):
    contexto = {"vehiculos":listado_vehiculo()}
    return render(request, "vehi.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.delete_servicios', login_url='/iniciar/')
def eliminar_esta(request, id):
    mensaje = ""
    try:
        es = Estado.objects.get(estado_ser = id)
        es.delete()
        mensaje = "Estado eliminado"
    except:
        mensaje = "Error al eliminar la estado"

    contexto = {
        "estados":listado_estado(), "mensaje":mensaje
    }
    return render(request, "estado.html", contexto)


#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.delete_servicios', login_url='/iniciar/')
def eliminar_vehi(request, id):
    mensaje = ""
    try:
        veh = Vehiculo.objects.get(cate_vehi = id)
        veh.delete()
        mensaje = "Vehiculo eliminado"
    except:
        mensaje = "Error al eliminar el vehiculo"

    contexto = {
        "vehiculos":listado_vehiculo(), "mensaje":mensaje
    }
    return render(request, "vehi.html", contexto)

#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.change_servicios', login_url='/iniciar/')
def modificar(request):
    mensaje = ""
    if request.POST:
        nombre = request.POST.get("nombre_servicio")
        precio = request.POST.get("precio_servicio")
        cate = request.POST.get("categoria")
        obj_categoria = Cate_ser.objects.get(tipo_ser = cate)
        try:
            ser = Servicios.objects.get(nombre_ser = nombre)
            ser.nombre_ser = nombre
            ser.precio_ser = precio
            ser.categoria_ser = obj_categoria
            ser.save()
            mensaje = "Servicio modificado"
        except:
            mensaje = "Servicio no modificado"
        
    data = {'categorias':listado_categorias(), 'servicios':listado_servicios(), "mensaje":mensaje}
    return render(request, "modificar.html", data)

#---------------------------------------------------------------

def modificar_c(request):
    mensaje = ""
    if request.POST:
        id_contrato = request.POST.get("id_contrato")
        estado_contrato = request.POST.get("estado")
        obj_esta = Estado.objects.get(estado_ser = estado_contrato)
        try:
            con = Contrato_ser.objects.get(id_contrato = id_contrato)
            con.estado_es = obj_esta
            con.save()
            mensaje = "Contrato modificado"
        except:
            mensaje = "Contrato no modificado"
        
    data = {'contratos':listado_contratos(), "estados":listado_estado(), "vehiculos":listado_vehiculo(), 
            "servicios":listado_servicios(), "mensaje":mensaje}
    return render(request, "modificar_con.html", data) 


#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.delete_servicios', login_url='/iniciar/')
def eliminar(request, id):
    mensaje = ""
    try:
        ser = Servicios.objects.get(nombre_ser = id)
        ser.delete()
        mensaje = "Servicio eliminado"
    except:
        mensaje = "Error al eliminar el servicio"

    contexto = {
        "categorias":listado_categorias(), "servicios":listado_servicios(), "mensaje":mensaje
    }
    return render(request, "agregar_servicios.html", contexto)

#---------------------------------------------------------------




#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.view_servicios',login_url='/iniciar/')
def buscar_modificar(request, id):
    try:
        ser = Servicios.objects.get(nombre_ser = id)
        contexto = {
            "categorias":listado_categorias(), "servicio":ser
        }
        return render(request, "modificar.html", contexto)
    except:
        mensaje = "Error al modificar el servicio"

    contexto = {
        "categorias":listado_categorias(), "servicios":listado_servicios(), "mensaje":mensaje
    }
    return render(request, "agregar_servicios.html", contexto)


#---------------------------------------------------------------

@login_required(login_url='/iniciar/')
@permission_required('carWash.view_servicios',login_url='/iniciar/')
def buscar_modificar_ad(request, id):
    try:
        con = Contrato_ser.objects.get(id_contrato = id)
        contexto = {
            "estados":listado_estado(), "contratos":listado_contratos(), "estado":listado_estado_def(), 
            "vehiculos":listado_vehiculo(), "categorias":listado_categorias(),  "contrato":con
        }
        return render(request, "modificar_con.html", contexto)
    except:
        mensaje = "Error al modificar el servicio"

    contexto = {
        "contratos":listado_contratos(), "estados":listado_estado(), "vehiculos":listado_vehiculo(),
        "categorias":listado_categorias(), "mensaje":mensaje
    }
    return render(request, "agenda_admin.html", contexto)

#######################################################

def export_csv(request):
    data = {}
    data={
        "contratos":listado_contratos(),
        "cantidad":contratos(),
        "completos":contratos_completos()
    }
    return render(request, 'csv.html', data)

def informe_text(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=informe.txt'

    contrato = Contrato_ser.objects.all()

    lines = []

    for contra in contrato:
        lines.append(f'Nombre cliente:{contra.id_contrato}\nFecha de contrato:{contra.fecha_ini}\nCliente:{contra.dueno}\nEstado_servicio:{contra.estado_es}\nServicio:{contra.servicio.precio_ser}\n\n\n\n')
    response.writelines(lines)
    return response
    
def informe_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=informe.csv'

    writer = csv.writer(response)

    contrato = Contrato_ser.objects.all()

    writer.writerow(['Numero de Contrato', 'Fecha de contrato', 'Cliente', 'Estado_servicio', 'Servicio'])

    for contra in contrato:
        writer.writerow([contra.id_contrato, contra.fecha_ini, contra.dueno, contra.estado_es, contra.servicio])

    return response    




#####################################################################


#---------------------------------------------------------------

# APARTADO DE PROCEDIMIENTOS ALMACENADOS

#---------------------------------------------------------------

def listado_servicios():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_SERVICIOS", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#---------------------------------------------------------------

def listado_categorias():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_CATEGORIAS", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#---------------------------------------------------------------

def listado_contratos():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_CONTRATOS", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#***************************************************************

def listado_vehiculo():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_VEHICULO", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#---------------------------------------------------------------

def listado_estado():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_ESTADO", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista
#---------------------------------------------------------------

def listado_estado_def():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_LISTAR_ESTADO_DEFECTO", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#---------------------------------------------------------------

def agregar_servicio(nombre_ser, precio_ser, categoria_ser_id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    salida = cursor.var(cx_Oracle.NUMBER)
    
    cursor.callproc("SP_AGREGAR_SERVICIOS", [nombre_ser, precio_ser, categoria_ser_id, salida])
    return salida.getvalue()


#---------------------------------------------------------------

def agregar_contrato(fecha_ini , dueno, estado_es_id, servicio_id, vehi_id):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    salida = cursor.var(cx_Oracle.NUMBER)
    
    cursor.callproc("SP_INSERTAR_CONTRATOS", [fecha_ini , dueno, estado_es_id, servicio_id, vehi_id, salida])
    return salida.getvalue()

#---------------------------------------------------------------

def agregar_categoria(tipo_ser):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    salida = cursor.var(cx_Oracle.NUMBER)
    
    cursor.callproc("SP_AGREGAR_CATEGORIAS", [tipo_ser, salida])
    return salida.getvalue()

#---------------------------------------------------------------

def agregar_estado(estado_ser):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    salida = cursor.var(cx_Oracle.NUMBER)
    
    cursor.callproc("SP_AGREGAR_ESTADOS", [estado_ser, salida])
    return salida.getvalue()

#---------------------------------------------------------------

def agregar_vehiculo(cate_vehi):
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    salida = cursor.var(cx_Oracle.NUMBER)
    
    cursor.callproc("SP_AGREGAR_VEHICULOS", [cate_vehi, salida])
    return salida.getvalue()

#---------------------------------------------------------------

def contratos():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_CONTRATOS", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista

#---------------------------------------------------------------

def contratos_completos():
    django_cursor = connection.cursor()
    cursor = django_cursor.connection.cursor()
    out_cur = django_cursor.connection.cursor()
    
    cursor.callproc("SP_CONTRA_COMPLETO", [out_cur])
    
    lista = []
    for fila in out_cur:
        lista.append(fila)
        
    return lista
