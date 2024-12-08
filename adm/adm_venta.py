from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.context_processors import request
from django.template.loader import get_template
from datetime import datetime
from decimal import Decimal

from core.funciones import normalizarTexto
from adm.models import vVenta, Cliente
# IMPORTACIONES DE FORMULARIOS
from adm.forms import DecimalForm
from core.forms import PersonaForm
from weasyprint import HTML, CSS
import os

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

        if action == 'abonardeuda':
            try:
                abono = Decimal(request.POST['decimal'])
                venta = vVenta.objects.get(id=request.POST['id'])

                if abono > (venta.totalventa - venta.abono):
                    return JsonResponse({'result': False, 'mensaje': 'Has ingresado una cantidad mayor a la deuda.', 'detalle':u'Ingresa una cantidad válida.'})

                venta.abono += abono
                venta.save()

                cliente = Cliente.objects.get(id=venta.cliente_id)
                if cliente.deuda_pendiente > abono:
                    cliente.deuda_pendiente -= abono
                    cliente.save()

                return JsonResponse({'result': True, 'mensaje': 'Se ha abonado a la deuda excitosamente'})
            except Exception as ex:
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
                    cliente = '_' + request.GET['cliente'].replace(' ', '_')

                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    pdf_dir = os.path.join(base_dir, 'static', 'pdf', 'reportes')

                    os.makedirs(pdf_dir, exist_ok=True)

                    file = os.path.join(pdf_dir, f'reporte_{fecha}{cliente}.pdf')

                    html_path = os.path.join(base_dir, 'templates', 'reportes', 'factura.html')

                    data['fecha'] = request.GET['fecha']
                    data['cliente'] = request.GET['cliente']

                    template = get_template(html_path)
                    html_content = template.render(data)

                    HTML(string=html_content).write_pdf(file)
                    return JsonResponse({"result": True, 'mensaje': 'Ha impreso la factura.'})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': 'Ha ocurrido un error generando la factura.', 'detalle': str(ex)})

        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas realizadas'
                data['activo'] = 2
                data['list'] = vVenta.objects.filter(status=True)
                return render(request, 'venta/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado{str(ex)}")
