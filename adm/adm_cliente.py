from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template

from adm.models import Cliente
from adm.forms import ClienteForm, DecimalForm

from core.funciones import normalizarTexto, obtenerPersonaCedula
from core.models import Persona

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    persona = None
                    existe = False
                    cedula = form.cleaned_data['cedula']
                    if cedula.isdigit() and len(cedula) == 10:
                        if Persona.objects.filter(cedula=cedula, status=True).exists():
                            existe = True
                            persona = Persona.objects.get(cedula=cedula, status=True)

                        if Cliente.objects.filter(persona__cedula=cedula, persona__status=True, status=True).exists():
                            return JsonResponse({'result': False, 'mensaje': u'Ya se encuentra registrado este cliente.', 'detalle':''})

                        celular = form.cleaned_data.get('celular')
                        if celular:
                            if not celular.isdigit() or len(celular) != 10:
                                return JsonResponse({'result': False, 'mensaje': u'Ha ocurrido un error al ingresar el número de TELÉFONO.', 'detalle': 'Asegúrese que sean 10 dígitos.'})

                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        apellido1 = normalizarTexto(form.cleaned_data['apellido1'])
                        apellido2 = normalizarTexto(form.cleaned_data.get('apellido2'))
                        direccion = normalizarTexto(form.cleaned_data.get('direccion'))
                        correo = form.cleaned_data.get('correo')

                        if not existe:
                            persona = Persona(
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
                        return JsonResponse({'result': True, 'mensaje':u'El cliente ha sido registrado en el sistema excitosamente.'})
                    else:
                        return JsonResponse({'result': False, 'mensaje': u'Ingrese una cédula válida.','detalle': ''})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con el registro del cliente.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    cliente = Cliente.objects.get(pk=request.POST['id'])
                    cedula = form.cleaned_data['cedula']
                    if cedula.isdigit() and len(cedula) == 10:
                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        apellido1 = normalizarTexto(form.cleaned_data['apellido1'])
                        apellido2 = normalizarTexto(form.cleaned_data['apellido2'])
                        direccion = normalizarTexto(form.cleaned_data['direccion'])
                        correo = form.cleaned_data.get('correo')

                        persona = None
                        existe = False

                        if Persona.objects.filter(cedula=cedula, status=True).exists():
                            existe = True
                            persona = Persona.objects.get(cedula=cedula, status=True)

                        if Cliente.objects.filter(persona__cedula=cedula, persona__status=True, status=True).exclude(persona__cedula=cliente.persona.cedula).exists():
                            return JsonResponse({'result': False, 'mensaje': u'Ya se encuentra registrado un cliente con esta cédula.', 'detalle':''})

                        celular = form.cleaned_data.get('celular')
                        if celular:
                            if not celular.isdigit() or len(celular) != 10:
                                return JsonResponse({'result': False, 'mensaje': u'Ha ocurrido un error al ingresar el número de TELÉFONO.', 'detalle': 'A  segúrese que sean 10 dígitos.'})

                        if not existe:
                            persona = Persona(
                                cedula=cedula,
                                nombre=nombre,
                                apellido1=apellido1,
                                apellido2=apellido2,
                                direccion=direccion,
                                celular=celular,
                                correo=correo,
                            )
                            persona.save()
                            cliente.persona = persona
                            cliente.save()
                            return JsonResponse({'result': True, 'mensaje': u'Se modificado los datos del cliente excitosamente.'})
                        persona.cedula = cedula
                        persona.nombre = nombre
                        persona.apellido1 = apellido1
                        persona.apellido2 = apellido2
                        persona.direccion = direccion
                        persona.celular = celular
                        persona.correo = correo
                        persona.save()

                        cliente.persona = persona
                        cliente.save()
                        return JsonResponse({'result': True, 'mensaje':u'Se modificado los datos del cliente excitosamente.'})
                    else:
                        return JsonResponse({'result': False, 'mensaje': u'Ingrese una cédula válida.','detalle': ''})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con la modificación de los datos del cliente.', 'detalle': str(ex)})

        if action == 'adddeuda':
            try:
                form = DecimalForm(request.POST)
                if form.is_valid():
                    deuda = form.cleaned_data['decimal']
                    cliente = Cliente.objects.get(pk=request.POST['id'])
                    cliente.deuda_pendiente += deuda
                    cliente.save()
                    return JsonResponse({'result': True, 'mensaje': 'Registrado la deuda excitosamente'})
                else:
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

        if action == 'del':
            try:
                cliente = Cliente.objects.get(pk=request.POST['id'])
                persona = Persona.objects.get(id=cliente.persona_id)
                if not persona.personatrabajador.filter(status=True).exists():
                    persona.status = False
                    persona.save()
                cliente.status = False
                cliente.save()
                return JsonResponse({'result': True, 'mensaje': 'Se ha eliminado el cliente excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        return render(request, 'exceptions/5XX.html', data)
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    form = ClienteForm() #el formulario para registrar clientes
                    template = get_template('modals/form_persona.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})

            if action == 'edit':
                try:
                    cliente = Cliente.objects.get(pk=request.GET['id'])
                    form = ClienteForm(initial={'nombre': cliente.persona.nombre, 'apellido1': cliente.persona.apellido1, 'apellido2': cliente.persona.apellido2,
                                                'cedula': cliente.persona.cedula, 'correo': cliente.persona.correo, 'direccion': cliente.persona.direccion,
                                                'celular': cliente.persona.celular})
                    template = get_template('modals/form_persona.html')
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

            if action == 'obtenercliente':
                try:
                    return obtenerPersonaCedula(request.GET['cedula'], data)
                except Exception as ex:
                    return JsonResponse({'result': False})

            return render(request, 'exceptions/5XX.html', data)
        else:
            try:
                data['title'] = u'Administración de Clientes'
                data['subtitle'] = u'Administre sus clientes'
                data['list'] = Cliente.objects.filter(persona__status=True, status=True).select_related('persona').order_by('-id')
                data['administracion'] = True
                data['adm_activo'] = 1
                return render(request, 'administracion/adm_clientes.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Clientes'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request, 'exceptions/5XX.html', data)
