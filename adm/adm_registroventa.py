import datetime
import json
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.db import transaction

from core.funciones import normalizarTexto

from adm.models import Producto, VentaDetalle, Venta, Cliente, Trabajador, KardexProducto, LoteProducto
from core.models import Persona

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, RegistroVentaForm, ClienteForm, RegistroTotalForm
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
                descuento = float(descuento) if descuento else 0

                venta = Venta(
                    cliente=cliente,
                    fecha_venta=datetime.datetime.now(),
                    descuento=descuento,
                    preciov=float(request.POST['preciov'][1:]),
                    detalle=request.POST['detalle'],
                )
                venta.save()

                for detalle in detalles:
                    lote = LoteProducto.objects.get(pk=detalle['id'])
                    cantidad = int(detalle['cantidad'])
                    preciou = Decimal(detalle['preciou'][1:])

                    ventadetalle = VentaDetalle(
                        venta=venta,
                        producto=lote.producto,
                        cantidad=cantidad,
                        preciou=preciou,
                        preciot=preciou * cantidad,
                    )
                    ventadetalle.save()

                    # Registrar el movimiento en el Kardex
                    kardex = KardexProducto(
                        producto=lote.producto,
                        tipo_movimiento=2,
                        cantidad=cantidad,
                        costo_unitario=lote.preciocompra,
                        precio_unitario=preciou,
                        lote=lote,
                    )
                    kardex.save()

                    # Actualizar la cantidad del lote
                    lote.cantidad -= cantidad
                    lote.save()
                return JsonResponse({"result": True, 'mensaje': u'Ha realizado la venta correctamente', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'cargarlotes':
                try:
                    producto = Producto.objects.get(pk=request.GET['id'])
                    lote = producto.loteproducto.filter(status=True, cantidad__gte=1)
                    selectLote = []
                    if lote:
                        for lt in lote:
                            selectLote.append(f'{lt.id}|{lt.producto} - ${lt.precioventa} x {lt.cantidad}')
                        return JsonResponse({"result": True, 'selectLote': selectLote})
                    else:
                        return JsonResponse({"result": True, 'mensaje': 'No hay lotes disponibles para este producto.'})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})

            if action == 'cargarprecio':
                try:
                    lote = LoteProducto.objects.get(pk=request.GET['id'])
                    precio = lote.precioventa
                    cantidad = lote.cantidad
                    return JsonResponse({"result": True, 'precio': precio, 'cantidad': cantidad})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})

            if action == 'obtenercliente':
                try:
                    persona = Persona.objects.get(cedula=request.GET['cedula'])
                    if persona.cliente.exists():
                        data['nombres'] = persona.nombre
                        data['nombre'] = persona.nombre
                        data['apellido1'] = persona.apellido1
                        data['apellido2'] = persona.apellido2
                        data['correo'] = persona.correo
                        data['celular'] = persona.celular
                        data['direccion'] = persona.direccion
                        return JsonResponse({'result': True, 'data': data})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})
        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas de productos'

                form = RegistroVentaForm()
                form2 = ClienteForm()
                form3 = RegistroTotalForm()

                form.fields['preciou'].widget.attrs['readonly'] = True
                form.fields['precios'].widget.attrs['readonly'] = True
                form3.fields['preciot'].widget.attrs['readonly'] = True
                form3.fields['preciosd'].widget.attrs['readonly'] = True

                data['form'] = form
                data['form2'] = form2
                data['form3'] = form3
                data['activo'] = 2
                return render(request, 'venta/registroventa.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado, {str(ex)}")
