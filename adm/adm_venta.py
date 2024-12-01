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

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'generarfacturapdf':
                try:
                    print(HTML.__module__)
                    file = r'C:/PycharmProjects/adm_mecanica/static/reportes/factura.pdf'
                    path = r'C:/PycharmProjects/adm_mecanica/templates/reportes/factura.html'
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
