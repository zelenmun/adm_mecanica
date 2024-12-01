from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from django import forms

from .forms import AddTrabajoForm, TrabajoDiaForm
from core.funciones import normalizarTexto

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm
from adm.models import Trabajo, TrabajoDia, Trabajador, Cliente

def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            try:
                if request.POST['trabajo']:
                    trabajo = Trabajo.objects.get(pk=request.POST['trabajo'])
                    precio = float(request.POST['precio'][1:])
                    nprecio = request.POST['nprecio']

                    trabajador = None
                    if request.POST['trabajador']:
                        if Trabajador.objects.get(pk=request.POST['trabajador']).exists():
                            trabajador = Trabajador.objects.get(pk=request.POST['trabajador'])

                    cliente = None
                    if request.POST['cliente']:
                        if Cliente.objects.get(pk=request.POST['cliente']).exists():
                            cliente = Cliente.objects.get(pk=request.POST['cliente'])

                    detalle = normalizarTexto(request.POST['detalle'])

                    if nprecio:
                        precio = float(request.POST['nprecio'])

                    workday = TrabajoDia(
                        precio=precio,
                        trabajo=trabajo,
                        trabajador=trabajador,
                        cliente=cliente,
                        detalle=detalle
                    )
                    workday.save()
                    hoy = datetime.now()
                    return JsonResponse({"result": True, 'mensaje': u'Has agregado un nuevo trabajo el dia de hoy', 'detalle': f'{hoy.strftime("%d/%m/%Y %H:%M")}'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = TrabajoDiaForm(request.POST)
                if form.is_valid():
                    workday = TrabajoDia.objects.get(pk=request.POST['id'])

                    workday.trabajo = form.cleaned_data['trabajo']
                    workday.precio = form.cleaned_data['precio']
                    workday.cliente = form.cleaned_data['cliente']
                    workday.trabajador = form.cleaned_data['trabajador']
                    workday.detalle = normalizarTexto(form.cleaned_data['detalle'])

                    workday.save()
                    hoy = datetime.now()
                    return JsonResponse({"result": True, 'mensaje': u'Has modificado el registro excitosamente', 'detalle': f'{hoy.strftime("%d/%m/%Y %H:%M")}'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})

        if action == 'del':
            try:
                workday = TrabajoDia.objects.get(pk=request.POST['id'])
                workday.status = False
                workday.save()
                return JsonResponse({"result": True, 'mensaje': u'Has eliminado el registro excitosamente.', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})


        return HttpResponse(f"Método no soportado")
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    form = AddTrabajoForm()
                    data['form'] = form
                    data['action'] = action
                    template = get_template("modals/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'edit':
                try:
                    workday = TrabajoDia.objects.get(pk=request.GET['id'])
                    form = TrabajoDiaForm(initial={'trabajo': workday.trabajo, 'precio': workday.precio, 'detalle': workday.detalle, 'cliente': workday.cliente, 'trabajador': workday.trabajador})
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'obtenerprecio':
                try:
                    trabajo = Trabajo.objects.get(pk=request.GET['id'])
                    return JsonResponse({"result": True, 'precio': trabajo.precio})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el valor.', 'detalle': str(ex)})
            return HttpResponse(f"Método no soportado, {str(ex)}")
        else:
            try:
                data['form'] = form = AddTrabajoForm()
                form.fields['precio'].widget.attrs['readonly'] = True

                data['title'] = u'Servicios de Mecánica'
                data['subtitle'] = u'Registra los servicios de mecánica realizados'
                data['list'] = TrabajoDia.objects.filter(status=True)

                data['activo'] = 1
                return render(request, 'servicios/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado, {str(ex)}")
