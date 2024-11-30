from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

from adm.models import Cliente
from adm.forms import ClienteForm, DecimalForm

from core.funciones import normalizarTexto
from core.models import Persona

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    cedula = form.cleaned_data['cedula']
                    if cedula.isdigit():
                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        apellido1 = normalizarTexto(form.cleaned_data['apellido1'])
                        apellido2 = normalizarTexto(form.cleaned_data.get('apellido2'))
                        direccion = normalizarTexto(form.cleaned_data.get('direccion'))
                        celular = form.cleaned_data.get('celular')
                        correo = form.cleaned_data.get('correo')
                        if Persona.objects.filter(cedula=cedula, status=True).exists():
                            return JsonResponse({'result': False, 'mensaje': u'Ya se encuentra registrado este cliente.', 'detalle':''})
                        persona = Persona.objects.create(
                            cedula=cedula,
                            nombre=nombre,
                            apellido1=apellido1,
                            apellido2=apellido2,
                            direccion=direccion,
                            celular=celular,
                            correo=correo,
                        )
                        persona.save()
                        cliente = Cliente(persona=persona)
                        cliente.save()
                        return JsonResponse({'result': True, 'mensaje':u'Se ha registrado correctamente.'})
                    else:
                        return JsonResponse({'result': False, 'mensaje': u'Ingrese una cédula válida.','detalle': ''})
                return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': True, 'mensaje':u'Parece que ha ocurrido un error con el registro del cliente.', 'detalle': str(ex)})

        if action == 'adddeuda':
            try:
                form = DecimalForm(request.POST)
                if form.is_valid():
                    deuda = form.cleaned_data['decimal']
                    cliente = Cliente.objects.get(pk=request.POST['id'])
                    cliente.deuda_pendiente += deuda
                    cliente.save()
                    return JsonResponse({'result': True, 'mensaje': 'Registrado la deuda excitosamente'})
                return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'saldardeuda':
            try:
                cliente = Cliente.objects.get(pk=request.POST['id'])
                cliente.deuda_pendiente = 0
                cliente.save()
                return JsonResponse({'result': True, 'mensaje': 'Deuda Saldada!'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    form = ClienteForm() #el formulario para registrar clientes
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})

            if action == 'adddeuda':
                try:
                    form = DecimalForm()
                    form.fields['decimal'].widget.attrs['placeholder'] = 'Registrar deuda'
                    form.fields['decimal'].label = u'Deuda'
                    data['form'] = form
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({'result': False, 'mensaje': u'No se pudo obtener el formulario.', 'detalle':str(ex)})
        else:
            try:
                data['title'] = u'Administración de Clientes'
                data['subtitle'] = u'Administre sus clientes'
                data['list'] = Cliente.objects.filter(persona__status=True, status=True).select_related('persona').order_by('-id')
                data['administracion'] = True
                data['adm_activo'] = 1
                return render(request, 'administracion/adm_clientes.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
