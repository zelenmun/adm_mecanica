from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
import xlwt
from xlwt import XFStyle, easyxf
from adm.models import (KardexProducto, vVenta, VentaProductoDetalle, VentaAdicionalDetalle, VentaServicioDetalle,
                        GastoNoOperativo)
from datetime import datetime, timedelta, date
def view(request):
    data = {}
    hoy = datetime.now().date()  # Obtiene solo la fecha (sin hora)
    data['hoy'] = hoy
    lunes = obtener_rango_semana_actual()
    if request.method == 'POST':
        action = request.POST['action']
    else:
        if 'action' in request.GET:
            action = request.GET['action']

            if action == 'generarcuentasdia':
                try:
                    response = HttpResponse(content_type="application/ms-excel")
                    fechaname = hoy.strftime('%Y_%m_%d')
                    response['Content-Disposition'] = f'attachment; filename=excel_dia_{fechaname}.xls'
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('Sheetname')
                    estilo = xlwt.easyxf('font: height 300, name Arial, colour_index black, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;')
                    estilo_general = xlwt.easyxf('font: height 220, name Arial; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
                    formato_fecha = xlwt.easyxf('align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;', num_format_str='yyyy/mm/dd')
                    estilo_cabecera = xlwt.easyxf('font: height 220, name Arial; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray_ega;')

                    ws.write_merge(0, 0, 0, 8,'TALLER DE SERVICIO MECÁNICO Y VENTA DE REPUESTOS DE MOTOS LINEALES SUPER MOTO',estilo)

                    ws.write(2, 0, 'FECHA', estilo_general)
                    ws.write(2, 1, hoy, formato_fecha)

                    ws.col(0).width = 4000
                    ws.col(1).width = 12000
                    ws.col(2).width = 6000
                    ws.col(3).width = 8000
                    ws.col(4).width = 4000
                    ws.col(5).width = 4000
                    ws.col(6).width = 4000
                    ws.col(7).width = 4000
                    ws.col(8).width = 4000

                    ws.write(4, 0, 'ID', estilo_cabecera)
                    ws.write(4, 1, 'DETALLE', estilo_cabecera)
                    ws.write(4, 2, 'FECHA', estilo_cabecera)
                    ws.write(4, 3, 'CLIENTE', estilo_cabecera)
                    ws.write(4, 4, 'ABONO', estilo_cabecera)
                    ws.write(4, 5, 'SUBTOTAL', estilo_cabecera)
                    ws.write(4, 6, 'DESCUENTO', estilo_cabecera)
                    ws.write(4, 7, 'TOTAL', estilo_cabecera)
                    ws.write(4, 8, 'ESTADO', estilo_cabecera)

                    a = 4

                    date_format = xlwt.XFStyle()
                    date_format.num_format_str = 'yyyy/mm/dd'

                    #ventas = vVenta.objects.filter(status=True, fecha_creacion__date=hoy)
                    ventas = vVenta.objects.filter(status=True)

                    for venta in ventas:
                        a += 1
                        ws.write(a, 0, venta.id, estilo_general)  # ID
                        ws.write(a, 1, venta.obtener_detalles_excel(), estilo_general)  # Detalle
                        ws.write(a, 2, venta.fecha_venta.strftime('%Y-%m-%d'), formato_fecha)  # Fecha
                        ws.write(a, 3, str(venta.cliente.persona if venta.cliente else "N/A"), estilo_general)  # Cliente
                        ws.write(a, 4, venta.abono, estilo_general)  # Abono
                        ws.write(a, 5, venta.subtotalventa, estilo_general)  # Subtotal
                        ws.write(a, 6, venta.descuento, estilo_general)  # Descuento
                        ws.write(a, 7, venta.totalventa, estilo_general)  # Total
                        ws.write(a, 8, venta.get_estado_display(), estilo_general)  # Estado

                    wb.save(response)
                    return response
                except Exception as ex:
                    pass

        else:
            try:
                data['buscador'] = True
                data['title'] = f'Dashboard Mecánica | {hoy}'
                data['lunes'] = lunes

                totalservicios = calcular_total_servicios(hoy)
                totalrepuestos = calcular_total_repuestos(hoy)
                totaldetalles = calcular_total_detalles(hoy)
                totaldescuentos = calcular_total_descuentos(hoy)
                totalegresos = calcular_total_egreso(hoy)

                balancegeneral = (totalservicios + totalrepuestos + totaldetalles) - (totalegresos + totaldescuentos)

                data['totalservicios'] = f'{totalservicios}'
                data['totalrepuestos'] = f'{totalrepuestos}'

                data['balancegeneral'] = f'{balancegeneral}'
                data['totalegresos'] = f'{totalegresos}'
                data['totaldescuentos'] = f'{totaldescuentos}'
                data['dashboardatras'] = True

                ventasdia = vVenta.objects.filter(status=True, fecha_venta__date=hoy)
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
        resultado = vVenta.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('descuento'))
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