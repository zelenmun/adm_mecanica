from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.context_processors import request
from django.template.loader import get_template
from datetime import datetime
from decimal import Decimal
from django.core.serializers import serialize
from core.funciones import normalizarTexto
from adm.models import vVenta, Cliente, ESTADO_VENTA
# IMPORTACIONES DE FORMULARIOS
from adm.forms import DecimalForm
from core.forms import PersonaForm
from weasyprint import HTML, CSS
import os
from django.db import transaction
import locale

def view(request):
    data = {}
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

        if action == 'abonardeuda':
            try:
                with transaction.atomic():
                    abono = Decimal(request.POST['decimal'])
                    venta = vVenta.objects.get(id=request.POST['id'])

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

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

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
                    venta = vVenta.objects.get(id=request.GET['id'])

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

        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas realizadas'

                estado = request.GET.get('estado', None)
                data['fechafiltro'] = fechafiltro = request.GET.get('fechafiltro', None)
                ventas = vVenta.objects.filter(status=True)

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
                return HttpResponse(f"Método no soportado{str(ex)}")
