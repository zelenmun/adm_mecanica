import datetime
import json
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.db import transaction

from core.funciones import normalizarTexto, obtenerClienteCedula

from adm.models import Producto, VentaDetalle, Venta, Cliente, Trabajador, KardexProducto, LoteProducto, TrabajoDia, \
    TrabajoDiaDetalle, Trabajo
from core.models import Persona

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, RegistroServicioForm, ClienteForm, RegistroTotalForm
from core.forms import PersonaForm

@transaction.atomic
def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                with transaction.atomic():
                    tabla = request.POST['tabla']
                    detalles = json.loads(tabla)
                    cedula = request.POST['cedula']
                    cliente = None
                    if cedula:
                        cliente = Cliente.objects.get(persona__cedula=cedula)
                    descuento = request.POST['descuento']
                    descuento = float(descuento) if descuento else 0
                    trabajador = request.POST['trabajador']
                    trabajador = trabajador if trabajador else None
                    workday = TrabajoDia(
                        trabajador=trabajador,
                        cliente=cliente,
                        detalle=request.POST['detalle'],
                        descuento=descuento,
                        preciot=Decimal(request.POST['preciot'][1:]),
                        fecha_servicio=datetime.datetime.now(),
                    )
                    workday.save()

                    for detalle in detalles:
                        trabajo = Trabajo.objects.get(pk=detalle['id'])
                        cantidad = int(detalle['cantidad'])
                        preciou = Decimal(detalle['preciou'][1:])
                        preciot = Decimal(detalle['total'][1:])

                        workdaydetail = TrabajoDiaDetalle(
                            trabajodia=workday,
                            trabajo=trabajo,
                            cantidad=cantidad,
                            preciou=preciou,
                            preciot=preciot
                        )
                        workdaydetail.save()
                    return JsonResponse({"result": True, 'mensaje': u'Ha realizado la venta correctamente', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        if action == 'del':
            try:
                with transaction.atomic():
                    trabajo = Trabajo.objects.get(pk=request.POST['id'])
                    trabajo.status = False
                    trabajo.save()
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, "mensaje": 'Parece que ha ocurrido un problema al eliminar el registro', 'detalle': str(ex)})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'obtenerprecio':
                try:
                    trabajo = Trabajo.objects.get(pk=request.GET['id'])
                    return JsonResponse({"result": True, 'precio': trabajo.precio})
                except Exception as ex:
                    return JsonResponse(
                        {"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})

            if action == 'obtenercliente':
                return obtenerClienteCedula(request.GET['cedula'])
        else:
            try:
                data['title'] = u'Servicios'
                data['subtitle'] = u'Registro de servicios brinados'

                form = RegistroServicioForm()
                form2 = ClienteForm()
                form3 = RegistroTotalForm()

                form.fields['preciou'].widget.attrs['readonly'] = True
                form.fields['precios'].widget.attrs['readonly'] = True
                form3.fields['preciot'].widget.attrs['readonly'] = True
                form3.fields['preciosd'].widget.attrs['readonly'] = True

                data['form'] = form
                data['form2'] = form2
                data['form3'] = form3
                data['activo'] = 1
                return render(request, 'servicios/registroservicio.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado, {str(ex)}")
