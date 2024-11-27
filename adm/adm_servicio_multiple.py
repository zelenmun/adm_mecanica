from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

from core.funciones import normalizarTexto

from adm.models import Producto

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, MultipleServiceForm
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'obtenerprecio':
                try:
                    producto = Producto.objects.get(pk=request.GET['id'])
                    return JsonResponse({"result": True, 'precio': producto.precio})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})
        else:
            try:
                data['title'] = u'Ventas'
                data['subtitle'] = u'Registro de múltiples ventas'

                form = MultipleServiceForm()
                form.fields['preciou'].widget.attrs['readonly'] = True
                form.fields['precios'].widget.attrs['readonly'] = True
                form.fields['preciot'].widget.attrs['readonly'] = True
                data['form'] = form

                return render(request, 'servicios/multiple.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
