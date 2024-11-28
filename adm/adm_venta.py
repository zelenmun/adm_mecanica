import datetime
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.db import transaction

from core.funciones import normalizarTexto

from adm.models import Producto, VentaDetalle, Venta, Cliente, Trabajador
from core.models import Persona

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, MultipleServiceForm, ClienteForm
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                tabla = request.POST['tabla']
                detalles = json.loads(tabla)
                cedula = request.POST['cedula']
                cliente = None
                if cedula:
                    cliente = Cliente.objects.get(persona__cedula=cedula)

                descuento = request.POST['descuento']
                if descuento:
                    float(request.POST['descuento'])
                else:
                    descuento = 0
                venta = Venta(
                    cliente=cliente,
                    fecha_venta=datetime.datetime.now(),
                    descuento=descuento,
                    preciov=float(request.POST['preciov'][1:]),
                    detalle=request.POST['detalle'],
                )
                venta.save()

                for detalle in detalles:
                    ventadetalle = VentaDetalle(
                        venta=venta,
                        producto=Producto.objects.get(pk=detalle['id']),
                        cantidad=int(detalle['cantidad']),
                        preciou=float(detalle['preciou'][1:]),
                        preciot=float(detalle['total'][1:]),
                    )
                    ventadetalle.save()
                return JsonResponse({"result": True, 'mensaje': u'Ha realizado la venta correctamente', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'obtenerprecio':
                try:
                    producto = Producto.objects.get(pk=request.GET['id'])
                    return JsonResponse({"result": True, 'precio': producto.precio})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})
            if action == 'obtenercliente':
                try:
                    persona = Persona.objects.get(cedula=request.GET['cedula'])
                    if persona.clientes.exists():
                        data['nombres'] = persona.nombre
                        data['nombre'] = persona.nombre
                        data['apellido1'] = persona.apellido1
                        data['apellido2'] = persona.apellido2
                        data['correo'] = persona.correo
                        data['celular'] = persona.celular
                        data['direccion'] = persona.direccion
                        return JsonResponse({'result': True, 'data': data})
                    return JsonResponse({'result':False})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})
        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de múltiples ventas'

                form = MultipleServiceForm()
                form2 = ClienteForm()
                form.fields['preciou'].widget.attrs['readonly'] = True
                form.fields['precios'].widget.attrs['readonly'] = True
                form.fields['preciot'].widget.attrs['readonly'] = True
                data['form'] = form
                data['form2'] = form2
                data['activo'] = 2
                return render(request, 'venta/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
