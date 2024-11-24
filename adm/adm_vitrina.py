from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

# IMPORTACIONES DE FORMULARIOS
from adm.forms import TextoForm
from adm.models import Vitrina
from core.funciones import normalizarTexto


def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = TextoForm(request.POST)
                if form.is_valid():
                    codigo = normalizarTexto(form.cleaned_data['texto'])
                    if Vitrina.objects.filter(codigo=codigo, status=True).exists():
                        return JsonResponse({'result': False, 'mensaje': u'Ya existe un registro con este código.', 'detalle':''})
                    vitrina = Vitrina(codigo=codigo)
                    vitrina.save()
                    return JsonResponse({'result': True, 'mensaje':u'Se ha ingresado correctamente la vitrina.'})
                return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': True, 'mensaje':u'Parece que ha ocurrido un error con el registro de la vitrina.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = TextoForm(request.POST)
                if form.is_valid():
                    vitrina = Vitrina.objects.get(pk=request.POST['id'])
                    codigo = normalizarTexto(form.cleaned_data['texto'])
                    if Vitrina.objects.filter(codigo=codigo, status=True).exclude(pk=vitrina.id).exists():
                        return JsonResponse({'result': False, 'mensaje': u'Ya existe un registro con este código.', 'detalle': ''})
                    vitrina.codigo = codigo
                    vitrina.save()
                    return JsonResponse({'result': True, 'mensaje':u'Se ha editado correctamente la vitrina.'})
                return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': True, 'mensaje':u'Parece que ha ocurrido un error con la edición de la vitrina.', 'detalle': str(ex)})

        if action == 'del':
            try:
                vitrina = Vitrina.objects.get(pk=request.POST['id'])
                if vitrina.vitrina_producto.exists():
                    return JsonResponse({'result': False, 'mensaje': u'No se puede eliminar una vitrina que contiene productos.', 'detalle':''})
                vitrina.status = False
                vitrina.save()
                return JsonResponse({'result': True, 'mensaje': u'Se ha eliminado correctamente la vitrina.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error al eliminar la vitrina.', 'detalle': str(ex)})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    form = TextoForm()
                    form.fields['texto'].widget.attrs['placeholder'] = 'Código de la vitrina'
                    form.fields['texto'].label = u'Código'
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'edit':
                try:
                    vitrina = Vitrina.objects.get(pk=request.GET['id'])
                    form = TextoForm(initial={'texto': vitrina.codigo})
                    form.fields['texto'].widget.attrs['placeholder'] = 'Código de la vitrina'
                    form.fields['texto'].label = u'Código'
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})
        else:
            try:
                data['title'] = u'Administración de Vitrinas'
                data['subtitle'] = u'Administre sus vitrinas'
                data['list'] = Vitrina.objects.filter(status=True)
                return render(request, 'administracion/adm_vitrinas.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
