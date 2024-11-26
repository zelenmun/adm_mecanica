from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from core.funciones import normalizarTexto
# IMPORTACIONES DE FORMULARIOS
from adm.forms import TrabajoForm
from adm.models import Trabajo

def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            try:
                form = TrabajoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['nombre'])
                    precio = form.cleaned_data['precio']
                    detalle = normalizarTexto(form.cleaned_data['detalle'])
                    if Trabajo.objects.filter(nombre=nombre, status=True).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Ya existe un trabajo con ese nombre.', 'detalle':''})
                    trabajo = Trabajo(nombre=nombre, precio=precio, detalle=detalle)
                    trabajo.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado la categoría excitosamente'})
                return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    form = TrabajoForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'edit':
                try:
                    trabajo = Trabajo.objects.get(pk=request.GET['id'])
                    form = TrabajoForm(initial={'nombre': trabajo.nombre, 'precio': trabajo.precio, 'detalle': trabajo.detalle})
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

        else:
            try:
                data['title'] = u'Administración de Trabajos'
                data['subtitle'] = u'Administre sus servicios de mecánica'
                data['palabraclave'] = u'Trabajo'
                data['list'] = Trabajo.objects.filter(status=True)
                return render(request, 'administracion/adm_trabajos.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
