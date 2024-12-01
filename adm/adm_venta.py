from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.context_processors import request
from django.template.loader import get_template

from core.funciones import normalizarTexto
from adm.models import Venta
# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm
from core.forms import PersonaForm
from weasyprint import HTML
import os
def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'generarfacturapdf':
                try:
                    fecha = request.GET['fecha'].replace('-', '_')
                    cliente = request.GET['cliente'].replace(' ', '_')

                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

                    pdf_dir = os.path.join(base_dir, 'static', 'pdf', 'reportes')
                    file = os.path.join(pdf_dir, f'reporte_{fecha}{cliente}.pdf')

                    os.makedirs(pdf_dir, exist_ok=True)

                    path = os.path.join(base_dir, 'templates', 'reportes', 'factura.html')

                    HTML(filename=path).write_pdf(file)
                    return JsonResponse({"result": True, 'mensaje': 'Ha impreso la factura.'})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': 'Ha ocurrido un error generando la factura.', 'detalle': str(ex)})

        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de ventas realizadas'
                data['activo'] = 2
                data['list'] = Venta.objects.filter(status=True)
                return render(request, 'venta/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado{str(ex)}")
