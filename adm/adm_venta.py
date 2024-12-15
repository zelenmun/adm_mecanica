from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Sum, Q
from django.template.loader import get_template
from datetime import datetime
from decimal import Decimal
import xlwt
from django.core.serializers import serialize
from core.funciones import normalizarTexto
from adm.models import Venta, Cliente, ESTADO_VENTA, LoteProducto, KardexProducto
# IMPORTACIONES DE FORMULARIOS
from adm.forms import DecimalForm
from weasyprint import HTML, CSS
import os
from django.db import transaction
import locale

def view(request):
    data = {}
    hoy = datetime.now().date()  # Obtiene solo la fecha (sin hora)
    data['hoy'] = hoy
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

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

        if action == 'del':
            try:
                venta = Venta.objects.get(pk=request.POST['id'])
                venta.status = False
                venta.save()

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
                return JsonResponse({'result': True})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje': u'Parece que ha ocurrido un error al eliminar el registro.', 'detalle': str(ex)})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'excelfechaestado':
                try:
                    fechafiltro = request.GET['fecha']
                    estado = request.GET['estado']
                    filtro = Q(status=True)
                    fecha_formateada = u'todos_los_registros'

                    if estado != 'None' and estado != '0':
                        filtro &= Q(estado=estado)
                        if estado == '1':
                            estado = u'pendientes'
                        else:
                            estado = u'pagados'
                    else:
                        estado = u'todos_los_estados'

                    if fechafiltro != 'None' and fechafiltro != '':
                        fechafiltro = datetime.strptime(request.GET['fecha'], "%Y-%m-%d")
                        fecha_formateada = fechafiltro.strftime("%Y_%m_%d")
                        filtro &= Q(fecha_creacion__date=fechafiltro)

                    response = HttpResponse(content_type="application/ms-excel")
                    response['Content-Disposition'] = f'attachment; filename=excel_{fecha_formateada}_{estado}.xls'
                    wb = xlwt.Workbook()
                    ws = wb.add_sheet('Sheetname')

                    wb.set_colour_RGB(0x21, 180, 198, 231)

                    estilo = xlwt.easyxf('font: height 300, name Calibri, colour_index black, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;')
                    estilo_general = xlwt.easyxf('font: height 220, name Calibri; align: wrap on, vert centre, horiz left; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
                    formato_fecha = xlwt.easyxf('font: height 220, name Calibri; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;',num_format_str='yyyy/mm/dd')
                    formato_fecha2 = xlwt.easyxf('font: height 220, name Calibri, bold on; align: wrap on, vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color 0x21;',num_format_str='yyyy/mm/dd')
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

                    ws.write_merge(a, a, 0, 8, 'TALLER DE SERVICIO MECÁNICO Y VENTA DE REPUESTOS DE MOTOS LINEALES SUPER MOTO', estilo)

                    a += 2

                    ws.write(a, 0, 'FECHA', formato_fecha2)
                    ws.write(a, 1, fechafiltro, formato_fecha2)

                    a += 2

                    ws.write_merge(a, a, 0, 8, 'TABLA DE INFORMACIÓN DE VENTAS', estilo_cabecera2)

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

                    ventas = Venta.objects.filter(filtro)

                    for venta in ventas:
                        a += 1
                        ws.write(a, 0, venta.id, estilo_general)
                        ws.write(a, 1, venta.obtener_detalles_excel(), estilo_general)
                        ws.write(a, 2, venta.fecha_venta.strftime('%Y-%m-%d'), formato_fecha)
                        ws.write(a, 3, str(venta.cliente.persona if venta.cliente else "CONSUMIDOR FINAL"),
                                 estilo_general)  # Cliente
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
                    wb.save(response)
                    return response
                except Exception as ex:
                    data['exception'] = str(ex)
                    pass

            if action == 'abonardeuda':
                try:
                    form = DecimalForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'generarfacturapdf':
                try:
                    fecha = str(datetime.now().timestamp()).replace('.', '')
                    fechaactual = datetime.now()
                    fecha_formateada = fechaactual.strftime("%A, %d de %B de %Y, %H:%M")
                    venta = Venta.objects.get(id=request.GET['id'])

                    # Obtener detalles de la venta
                    detalleprodcto = venta.detalleproducto.filter(status=True)
                    detalleservicio = venta.detalleservicio.filter(status=True)
                    detalleadicional = venta.detalleadicional.filter(status=True)

                    data['list1'] = detalleprodcto
                    data['list2'] = detalleservicio
                    data['list3'] = detalleadicional
                    data['fecha'] = venta.fecha_venta
                    data['totalventa'] = venta.totalventa
                    data['subtotalventa'] = venta.subtotalventa
                    data['descuento'] = venta.descuento
                    data['venta'] = venta
                    data['pendiente'] = venta.totalventa - venta.abono
                    data['fechaactual'] = fecha_formateada

                    persona = 'CONSUMIDOR FINAL'

                    if venta.cliente_id:
                        cliente = Cliente.objects.get(id=venta.cliente_id)
                        persona = cliente.persona

                    data['persona'] = persona

                    # Generación de contenido HTML
                    html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates', 'reportes', 'factura.html')
                    template = get_template(html_path)
                    html_content = template.render(data)

                    # Generar PDF en memoria
                    pdf_file = HTML(string=html_content).write_pdf()

                    # Crear la respuesta de descarga
                    response = HttpResponse(pdf_file, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="factura_{fecha}_{str(persona).replace(" ", "_")}.pdf"'

                    return response
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': 'Ha ocurrido un error generando la factura.', 'detalle': str(ex)})

            return render(request, 'exceptions/5XX.html', data)
        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas realizadas'

                data['estadofiltro'] = estado = request.GET.get('estado', None)
                data['fechafiltro'] = fechafiltro = request.GET.get('fechafiltro', None)
                ventas = Venta.objects.filter(status=True)

                if estado is not None:
                    estado = int(estado)
                    if estado > 0:
                        ventas = ventas.filter(estado=estado)
                if fechafiltro:
                    ventas = ventas.filter(fecha_creacion__date=fechafiltro)

                data['activo'] = 2
                data['list'] = ventas
                data['opciones'] = ESTADO_VENTA
                return render(request, 'venta/view.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Ventas'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request, 'exceptions/5XX.html', data)
