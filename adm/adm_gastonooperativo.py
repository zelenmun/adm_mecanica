from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from decimal import Decimal

# IMPORTACIONES DE FORMULARIOS
from adm.forms import GastoNoOperativoForm
from adm.models import GastoNoOperativo
from core.funciones import normalizarTexto


def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = GastoNoOperativoForm(request.POST)
                if form.is_valid():
                    titulo = normalizarTexto(form.cleaned_data['titulo'])
                    valor = Decimal(form.cleaned_data['valor'])
                    detalle = normalizarTexto(form.cleaned_data['detalle'])

                    gasto = GastoNoOperativo(titulo=titulo, valor=valor, detalle=detalle)
                    gasto.save()

                    return JsonResponse({'result': True, 'mensaje':u'Se ha registrado el gasto en sus cuentas.'})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con el registro de la vitrina.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = GastoNoOperativoForm(request.POST)
                if form.is_valid():
                    gasto = GastoNoOperativo.objects.get(pk=request.POST['id'])

                    titulo = normalizarTexto(form.cleaned_data['titulo'])
                    valor = Decimal(form.cleaned_data['valor'])
                    detalle = normalizarTexto(form.cleaned_data['detalle'])

                    gasto.titulo = titulo
                    gasto.valor = valor
                    gasto.detalle = detalle
                    gasto.save()
                    return JsonResponse({'result': True, 'mensaje':u'Se ha editado correctamente el gasto.'})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con la edición de la vitrina.', 'detalle': str(ex)})

        if action == 'del':
            try:
                gasto = GastoNoOperativo.objects.get(pk=request.POST['id'])
                gasto.status = False
                gasto.save()
                return JsonResponse({'result': True, 'mensaje': u'Se ha eliminado correctamente el gasto.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error al eliminar el gasto.', 'detalle': str(ex)})

        return render(request, 'exceptions/5XX.html', data)
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    form = GastoNoOperativoForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'edit':
                try:
                    gasto = GastoNoOperativo.objects.get(pk=request.GET['id'])
                    form = GastoNoOperativoForm(initial={'titulo': gasto.titulo, 'valor': gasto.valor, 'detalle': gasto.detalle})
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            return render(request,'exceptions/5XX.html', data)
        else:
            try:
                data['title'] = u'Gasto No Operativo'
                data['subtitle'] = u'Registra cualquier gasto que no forme parte del negocio'
                data['list'] = GastoNoOperativo.objects.filter(status=True)
                data['activo'] = 4
                return render(request, 'gasto_no_operativo/view.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Gasto No Operativo'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request,'exceptions/5XX.html', data)
