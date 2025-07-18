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
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado la el trabajo excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = TrabajoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['nombre'])
                    precio = form.cleaned_data['precio']
                    detalle = normalizarTexto(form.cleaned_data['detalle'])

                    trabajo = Trabajo.objects.get(pk=request.POST['id'])

                    if Trabajo.objects.filter(nombre=nombre, status=True).exclude(pk=trabajo.id).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Ya existe un trabajo con ese nombre.', 'detalle': ''})

                    trabajo.nombre = nombre
                    trabajo.precio = precio
                    trabajo.detalle = detalle
                    trabajo.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha modificado el registro excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        if action == 'del':
            try:
                trabajo = Trabajo.objects.get(pk=request.POST['id'])
                trabajo.status = False
                trabajo.save()
                return JsonResponse({"result": True, 'mensaje': u'Has eliminado el registro excitosamente.', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        return render(request, 'exceptions/5XX.html', data)
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

            return render(request, 'exceptions/5XX.html', data)
        else:
            try:
                data['title'] = u'Administración de Trabajos'
                data['subtitle'] = u'Administre sus servicios de mecánica'
                data['palabraclave'] = u'Trabajo'
                data['list'] = Trabajo.objects.filter(status=True)
                data['administracion'] = True
                data['adm_activo'] = 5
                return render(request, 'administracion/adm_trabajos.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Trabajo'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request, 'exceptions/5XX.html', data)
