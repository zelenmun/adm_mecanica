import datetime
import json
from decimal import Decimal

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.db import transaction

from core.funciones import normalizarTexto

from adm.models import Producto, VentaProductoDetalle, vVenta, Cliente, Trabajo, KardexProducto, LoteProducto, \
    VentaServicioDetalle, VentaAdicionalDetalle
from core.models import Persona

# IMPORTACIONES DE FORMULARIOS
from adm.forms import VentaProductoForm, ClienteForm, VentaServicioForm, VentaAdicionalForm, PagoClienteForm
from core.forms import PersonaForm


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
                    abono = Decimal(request.POST.get('abono', 0) or 0)
                    estado = 1

                    subtotal = 0

                    descuento = request.POST['descuento']
                    descuento = Decimal(descuento) if descuento else 0

                    for detalle in detalles:
                        subtotal = subtotal + Decimal(detalle['total'][1:])

                    total = Decimal(subtotal - descuento)

                    cliente = None
                    if cedula:
                        cliente = Cliente.objects.get(persona__cedula=cedula)
                        if abono < total:
                            cliente.deuda_pendiente += total - abono
                            cliente.save()

                    if total < 0:
                        total = 0

                    if abono >= total:
                        estado = 2


                    venta = vVenta(
                        cliente=cliente,
                        fecha_venta=datetime.datetime.now(),
                        descuento=descuento,
                        totalventa=total,
                        subtotalventa=subtotal,
                        estado=estado,
                        abono=abono
                    )
                    venta.save()

                    for detalle in detalles:
                        cantidad = int(detalle['cantidad'])
                        preciou = Decimal(detalle['preciou'][1:])
                        total = Decimal(detalle['total'][1:])

                        if detalle['tipo'] == 'PRODUCTO':
                            lote = LoteProducto.objects.get(pk=detalle['id'])
                            total = Decimal(lote.precioventa * cantidad)
                            ventadetalle = VentaProductoDetalle(
                                venta=venta,
                                producto=lote.producto,
                                lote=lote,
                                cantidad=cantidad,
                                preciounitario=lote.precioventa,
                                total=total,
                            )
                            ventadetalle.save()

                            # Registrar el movimiento en el Kardex
                            kardex = KardexProducto(
                                producto=lote.producto,
                                tipo_movimiento=2,
                                cantidad=cantidad,
                                costo_unitario=lote.preciocompra,
                                precio_unitario=lote.precioventa,
                                lote=lote,
                            )
                            kardex.save()

                            # Actualizar la cantidad del lote
                            if lote.cantidad >= cantidad:
                                lote.cantidad -= cantidad
                                lote.save()

                        if detalle['tipo'] == 'SERVICIO':
                            servicio = Trabajo.objects.get(pk=detalle['id'])
                            total = Decimal(cantidad * preciou)

                            ventadetalle = VentaServicioDetalle(
                                venta=venta,
                                servicio=servicio,
                                cantidad=cantidad,
                                total=total,
                            )
                            ventadetalle.save()

                        if detalle['tipo'] == 'ADICIONAL':
                            ventadetalle = VentaAdicionalDetalle(
                                venta=venta,
                                detalle=normalizarTexto(detalle['detalle']),
                                precio=total,
                            )
                            ventadetalle.save()
                    return JsonResponse({"result": True, 'mensaje': u'Ha realizado la venta correctamente', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        if action == 'edit':
            try:
                with transaction.atomic():
                    tabla = request.POST['tabla']
                    detalles = json.loads(tabla)
                    cedula = request.POST['cedula']
                    id = request.POST['id']
                    abono = Decimal(request.POST.get('abono', 0) or 0)
                    estado = 1

                    subtotal = 0

                    descuento = request.POST['descuento']
                    descuento = Decimal(descuento) if descuento else 0

                    for detalle in detalles:
                        subtotal = subtotal + Decimal(detalle['total'][1:])

                    total = Decimal(subtotal - descuento)

                    cliente = None
                    if cedula:
                        cliente = Cliente.objects.get(persona__cedula=cedula)
                        if abono < total:
                            cliente.deuda_pendiente += total - abono
                            cliente.save()

                    if total < 0:
                        total = 0

                    if abono >= total:
                        estado = 2

                    venta = vVenta.objects.get(pk=id)

                    if cliente is not None and venta.cliente is None:
                        venta.cliente = cliente

                    venta.fecha_venta = datetime.datetime.now()
                    venta.descuento = descuento
                    venta.totalventa = total
                    venta.subtotalventa = subtotal
                    venta.estado = estado
                    venta.abono = abono
                    venta.save()

                    venta.detalleservicio.filter(status=True).delete()
                    venta.detalleadicional.filter(status=True).delete()
                    prod = venta.detalleproducto.filter(status=True)
                    for p in prod:
                        lote = LoteProducto.objects.get(pk=p.lote_id)
                        kardex = KardexProducto(
                            producto=lote.producto,
                            tipo_movimiento=1,
                            cantidad=p.cantidad,
                            costo_unitario=lote.preciocompra,
                            precio_unitario=lote.precioventa,
                            lote=lote,
                        )
                        kardex.save()

                        lote.cantidad += p.cantidad
                        lote.save()

                    venta.detalleproducto.filter(status=True).delete()

                    for detalle in detalles:
                        cantidad = int(detalle['cantidad'])
                        preciou = Decimal(detalle['preciou'][1:])
                        total = Decimal(detalle['total'][1:])

                        if detalle['tipo'] == 'PRODUCTO':
                            lote = LoteProducto.objects.get(pk=detalle['id'])
                            total = Decimal(lote.precioventa * cantidad)
                            ventadetalle = VentaProductoDetalle(
                                venta=venta,
                                producto=lote.producto,
                                lote=lote,
                                cantidad=cantidad,
                                preciounitario=lote.precioventa,
                                total=total,
                            )
                            ventadetalle.save()

                            # Registrar el movimiento en el Kardex
                            kardex = KardexProducto(
                                producto=lote.producto,
                                tipo_movimiento=2,
                                cantidad=cantidad,
                                costo_unitario=lote.preciocompra,
                                precio_unitario=lote.precioventa,
                                lote=lote,
                            )
                            kardex.save()

                            # Actualizar la cantidad del lote
                            if (lote.cantidad >= cantidad):
                                lote.cantidad -= cantidad
                                lote.save()

                        if detalle['tipo'] == 'SERVICIO':
                            servicio = Trabajo.objects.get(pk=detalle['id'])
                            total = Decimal(cantidad * preciou)

                            ventadetalle = VentaServicioDetalle(
                                venta=venta,
                                servicio=servicio,
                                cantidad=cantidad,
                                total=total,
                            )
                            ventadetalle.save()

                        if detalle['tipo'] == 'ADICIONAL':
                            ventadetalle = VentaAdicionalDetalle(
                                venta=venta,
                                detalle=normalizarTexto(detalle['detalle']),
                                precio=total,
                            )
                            ventadetalle.save()
                    return JsonResponse({"result": True, 'mensaje': u'Ha modificado la venta correctamente', 'detalle': ''})
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

            if action == 'cargarprecioproducto':
                try:
                    lote = LoteProducto.objects.get(pk=request.GET['id'])
                    precio = lote.precioventa
                    cantidad = lote.cantidad
                    return JsonResponse({"result": True, 'precio': precio, 'cantidad': cantidad})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})

            if action == 'cargarprecioservicio':
                try:
                    servicio = Trabajo.objects.get(pk=request.GET['id'])
                    precio = servicio.precio
                    return JsonResponse({"result": True, 'precio': precio})
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

            if action == 'edit':
                try:
                    data['title'] = u'Ventas'
                    data['subtitle'] = u'Registro de ventas de productos'

                    data['id'] = id = request.GET['id']

                    list1 = vVenta.objects.get(id=id)

                    data['list1'] = list1
                    data['list2'] = list1.detalleproducto.filter(status=True)
                    data['list3'] = list1.detalleservicio.filter(status=True)
                    data['list4'] = list1.detalleadicional.filter(status=True)

                    form = VentaProductoForm()
                    form2 = VentaServicioForm()
                    form3 = VentaAdicionalForm()
                    form4 = ClienteForm()
                    form5 = PagoClienteForm(initial={'abono': list1.abono, 'descuento': list1.descuento})

                    form.fields['precioproducto'].widget.attrs['readonly'] = True
                    form2.fields['precioservicio'].widget.attrs['readonly'] = True

                    data['form'] = form
                    data['form2'] = form2
                    data['form3'] = form3
                    data['form4'] = form4
                    data['form5'] = form5
                    data['activo'] = 2

                    data['actionpy'] = u'edit'
                    return render(request, 'venta/registroventa.html', data)
                except Exception as ex:
                    return HttpResponse(request.path)

        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas de productos'

                form = VentaProductoForm()
                form2 = VentaServicioForm()
                form3 = VentaAdicionalForm()
                form4 = ClienteForm()
                form5 = PagoClienteForm()

                form.fields['precioproducto'].widget.attrs['readonly'] = True
                form2.fields['precioservicio'].widget.attrs['readonly'] = True

                data['form'] = form
                data['form2'] = form2
                data['form3'] = form3
                data['form4'] = form4
                data['form5'] = form5
                data['activo'] = 2
                data['actionpy'] = u'add'
                return render(request, 'venta/registroventa.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Registro de Ventas'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request, 'exceptions/5XX.html', data)
