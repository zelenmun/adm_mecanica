from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
import xlwt
from decimal import Decimal
from xlwt import XFStyle, easyxf
from adm.models import (KardexProducto, Venta, VentaProductoDetalle, VentaAdicionalDetalle, VentaServicioDetalle,
                        GastoNoOperativo, Producto, LoteProducto, Cliente)
from adm.forms import DecimalForm
from django.template.loader import get_template
from datetime import datetime, timedelta, date
from django.db import transaction
def view(request):
    data = {}
    hoy = datetime.now().date()  # Obtiene solo la fecha (sin hora)
    data['hoy'] = hoy
    lunes = obtener_rango_semana_actual()
    if request.method == 'POST':
        action = request.POST['action']

        if action == 'abonardeuda':
            try:
                with transaction.atomic():
                    abono = Decimal(request.POST['decimal'])
                    venta = Venta.objects.get(id=request.POST['id'])

                    if abono > (venta.totalventa - venta.abono):
                        return JsonResponse({'result': False, 'mensaje': 'Has ingresado una cantidad mayor a la deuda.', 'detalle':u'Ingresa una cantidad válida.'})

                    venta.abono += abono

                    if venta.abono == venta.totalventa:
                        venta.estado = 2

                    venta.save()

                    if venta.cliente:
                        cliente = Cliente.objects.get(id=venta.cliente_id)
                        if cliente.deuda_pendiente >= abono:
                            cliente.deuda_pendiente -= abono
                            cliente.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha abonado a la deuda excitosamente'})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al abonar a la venta.', 'detalle': str(ex)})

        if action == 'cancelarventa':
            try:
                venta = Venta.objects.get(pk=request.POST['id'])
                venta.status = False
                venta.save()

                # DETALLE PRODUCTO
                prod = venta.detalleproducto.filter(status=True)
                for p in prod:
                    lote = LoteProducto.objects.get(pk=p.lote_id)
                    kardex = KardexProducto(
                        producto=lote.producto,
                        tipo_movimiento=3,
                        cantidad=p.cantidad,
                        costo_unitario=0,
                        precio_unitario=0,
                        lote=lote,
                    )
                    kardex.save()

                    lote.cantidad += p.cantidad
                    lote.save()

                    p.status = False
                    p.save()

                # DETALLE SERVICIO
                servicios = VentaServicioDetalle.objects.filter(status=True, venta=venta)
                for servicio in servicios:
                    servicio.status = False
                    servicio.save()

                # DETALLE ADICIONAL
                adicionales = VentaAdicionalDetalle.objects.filter(status=True, venta=venta)
                for adicional in adicionales:
                    adicional.status = False
                    adicional.save()
                return JsonResponse({'result': True})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': u'Parece que ha ocurrido un error al eliminar el registro.', 'detalle': str(ex)})
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'abonardeuda':
                try:
                    form = DecimalForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'generarcuentasdia':
                try:
                    response = HttpResponse(content_type="application/ms-excel")
                    fechaname = hoy.strftime('%Y_%m_%d')
                    response['Content-Disposition'] = f'attachment; filename=excel_dia_{fechaname}.xls'
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('Sheetname')

                    wb.set_colour_RGB(0x21, 180, 198, 231)

                    estilo = xlwt.easyxf('font: height 300, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;')
                    estilo_general = xlwt.easyxf('font: height 220, name Calibri; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
                    formato_fecha = xlwt.easyxf('font: height 220, name Calibri; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;', num_format_str='yyyy/mm/dd')
                    formato_fecha2 = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;', num_format_str='yyyy/mm/dd')
                    # estilo_cabecera = xlwt.easyxf('font: height 220, name Arial; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25;')
                    # estilo_cabecera = xlwt.easyxf('font: height 220, name Arial; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color ice_blue;')
                    estilo_cabecera = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;')
                    estilo_cabecera2 = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;')
                    estilo_totales = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
                    estilo_totales2 = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
                    estilo_moneda = xlwt.easyxf('font: height 220, name Calibri; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')

                    estilo_moneda.num_format_str = '$#,##0.00'
                    estilo_totales.num_format_str = '$#,##0.00'

                    a = 1

                    ws.write_merge(a, a, 0, 8,'TALLER DE SERVICIO MECÁNICO Y VENTA DE REPUESTOS DE MOTOS LINEALES SUPER MOTO',estilo)

                    a += 2

                    ws.write(a, 0, 'FECHA', formato_fecha2)
                    ws.write(a, 1, hoy, formato_fecha2)

                    a += 2

                    ws.write_merge(a, a, 0, 8,'TABLA DE INFORMACIÓN DE VENTAS',estilo_cabecera2)

                    a += 1

                    ws.row(1).height = 1000
                    ws.col(0).width = 4000
                    ws.col(1).width = 14000
                    ws.col(2).width = 6000
                    ws.col(3).width = 8000
                    ws.col(4).width = 4000
                    ws.col(5).width = 4000
                    ws.col(6).width = 4000
                    ws.col(7).width = 4000
                    ws.col(8).width = 4000

                    ws.write(a, 0, 'ID', estilo_cabecera)
                    ws.write(a, 1, 'DETALLE', estilo_cabecera)
                    ws.write(a, 2, 'FECHA', estilo_cabecera)
                    ws.write(a, 3, 'CLIENTE', estilo_cabecera)
                    ws.write(a, 4, 'ABONO', estilo_cabecera)
                    ws.write(a, 5, 'SUBTOTAL', estilo_cabecera)
                    ws.write(a, 6, 'DESCUENTO', estilo_cabecera)
                    ws.write(a, 7, 'TOTAL', estilo_cabecera)
                    ws.write(a, 8, 'ESTADO', estilo_cabecera)

                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'

                    # ventas = Venta.objects.filter(status=True, fecha_creacion__date=hoy)
                    ventas = Venta.objects.filter(status=True)

                    for venta in ventas:
                        a += 1
                        ws.write(a, 0, venta.id, estilo_general)
                        ws.write(a, 1, venta.obtener_detalles_excel(), estilo_general)
                        ws.write(a, 2, venta.fecha_venta.strftime('%Y-%m-%d'), formato_fecha)
                        ws.write(a, 3, str(venta.cliente.persona if venta.cliente else "CONSUMIDOR FINAL"), estilo_general)  # Cliente
                        ws.write(a, 4, venta.abono, estilo_moneda)
                        ws.write(a, 5, venta.subtotalventa, estilo_moneda)
                        ws.write(a, 6, venta.descuento, estilo_moneda)
                        ws.write(a, 7, venta.totalventa, estilo_moneda)
                        ws.write(a, 8, venta.get_estado_display(), estilo_totales2)

                    a += 1

                    sumaabono = ventas.aggregate(total=Sum('abono'))
                    sumasubtotal = ventas.aggregate(total=Sum('subtotalventa'))
                    descuento = ventas.aggregate(total=Sum('descuento'))
                    totalventa = ventas.aggregate(total=Sum('totalventa'))

                    ws.write(a, 4, sumaabono['total'], estilo_totales)
                    ws.write(a, 5, sumasubtotal['total'], estilo_totales)
                    ws.write(a, 6, descuento['total'], estilo_totales)
                    ws.write(a, 7, totalventa['total'], estilo_totales)

                    # GASTO NO OPERATIVO -------------------------------------------------------------------------------
                    a += 3

                    ws.write_merge(a, a, 0, 4,'TABLA DE INFORMACIÓN DE GASTOS NO OPERATIVOS',estilo_cabecera2)

                    a += 1

                    ws.write(a, 0, 'ID', estilo_cabecera)
                    ws.write(a, 1, 'TITULO', estilo_cabecera)
                    ws.write(a, 2, 'FECHA', estilo_cabecera)
                    ws.write(a, 3, 'DETALLE', estilo_cabecera)
                    ws.write(a, 4, 'VALOR', estilo_cabecera)

                    # gastonooperativo = GastoNoOperativo.objects.filter(status=True, fecha_creacion__date=hoy)
                    gastonooperativo = GastoNoOperativo.objects.filter(status=True)

                    for gasto in gastonooperativo:
                        a += 1
                        ws.write(a, 0, gasto.id, estilo_general)
                        ws.write(a, 1, gasto.titulo, estilo_general)
                        ws.write(a, 2, gasto.fecha_creacion.strftime('%Y-%m-%d'), formato_fecha)
                        ws.write(a, 3, gasto.detalle, estilo_general)
                        ws.write(a, 4, gasto.valor,estilo_moneda)
                    a += 1

                    sumavalor = gastonooperativo.aggregate(total=Sum('valor'))
                    ws.write(a, 4, sumavalor['total'], estilo_totales)

                    # REPUESTOS ----------------------------------------------------------------------------------------
                    a += 3

                    ws.write_merge(a, a, 0, 5, 'TABLA DE INFORMACIÓN DE REPUESTOS COMPRADOS', estilo_cabecera2)

                    a += 1

                    ws.write(a, 0, 'ID', estilo_cabecera)
                    ws.write(a, 1, 'PRODUCTO', estilo_cabecera)
                    ws.write(a, 2, 'FECHA COMPRA', estilo_cabecera)
                    ws.write(a, 3, 'CANTIDAD', estilo_cabecera)
                    ws.write(a, 4, 'PRECIO UNITARIO', estilo_cabecera)
                    ws.write(a, 5, 'PRECIO TOTAL', estilo_cabecera)

                    # gastonooperativo = GastoNoOperativo.objects.filter(status=True, tipo_movimiento=1, fecha_creacion__date=hoy)
                    kardex = KardexProducto.objects.filter(status=True, producto__status=True, lote__status=True, tipo_movimiento=1)

                    for l in kardex:
                        a += 1
                        ws.write(a, 0, l.id, estilo_general)
                        ws.write(a, 1, l.producto.nombre, estilo_general)
                        ws.write(a, 2, l.fecha_movimiento.strftime('%Y-%m-%d'), formato_fecha)
                        ws.write(a, 3, l.cantidad, estilo_general)
                        ws.write(a, 4, l.costo_unitario, estilo_moneda)
                        ws.write(a, 5, l.costo_total, estilo_moneda)
                    a += 1

                    lcantidad = kardex.aggregate(total=Sum('cantidad'))
                    lcostounitario = kardex.aggregate(total=Sum('costo_unitario'))
                    lcostototal = kardex.aggregate(total=Sum('costo_total'))

                    ws.write(a, 3, lcantidad['total'], estilo_totales2)
                    ws.write(a, 4, lcostounitario['total'], estilo_totales)
                    ws.write(a, 5, lcostototal['total'], estilo_totales)
                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

            return render(request, 'exceptions/5XX.html', data)
        else:
            try:
                data['title'] = f'Dashboard Mecánica'
                data['subtitle'] = f'{hoy}'
                data['lunes'] = lunes

                totalservicios = calcular_total_servicios(hoy)
                totalrepuestos = calcular_total_repuestos(hoy)
                totaldetalles = calcular_total_detalles(hoy)
                totaldescuentos = calcular_total_descuentos(hoy)
                totalegresos = calcular_total_egreso(hoy)
                totalabonos = calcular_total_abonos(hoy)

                totalventas = totalservicios + totalrepuestos + totaldetalles

                balancegeneral = totalabonos - totalegresos

                data['totalventas'] = f'{totalventas:.2f}'
                data['totalabonos'] = f'{totalabonos:.2f}'

                data['balancegeneral'] = f'{balancegeneral:.2f}'
                data['totalegresos'] = f'{totalegresos:.2f}'
                data['totaldescuentos'] = f'{totaldescuentos:.2f}'
                data['dashboardatras'] = True

                ventasdia = Venta.objects.filter(status=True, fecha_venta__date=hoy)
                data['list'] = ventasdia

                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado {str(ex)}")

def calcular_total_servicios(hoy):
    try:
        resultado = VentaServicioDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('total'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_repuestos(hoy):
    try:
        resultado = VentaProductoDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('total'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_detalles(hoy):
    try:
        resultado = VentaAdicionalDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('precio'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_descuentos(hoy):
    try:
        resultado = Venta.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('descuento'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_abonos(hoy):
    try:
        resultado = Venta.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('abono'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_egreso(hoy):
    try:
        resultado = KardexProducto.objects.filter(status=True, tipo_movimiento=1,fecha_creacion__date=hoy).aggregate(total=Sum('costo_total'))
        resultado2 = GastoNoOperativo.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('valor'))

        valor1 = 0
        valor2 = 0
        if resultado['total']:
            valor1 = resultado['total']
        if resultado2['total']:
            valor2 = resultado2['total']
        return valor1 + valor2
    except Exception as e:
        return 0


def obtener_rango_semana_actual():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes