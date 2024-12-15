from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adm.forms import TrabajadorForm
from core.funciones import normalizarTexto, obtenerPersonaCedula
from core.models import Persona
from adm.models import Trabajador
from django.template.loader import get_template

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = TrabajadorForm(request.POST)
                if form.is_valid():
                    existe = False
                    persona = None
                    cedula = form.cleaned_data['cedula']

                    if cedula.isdigit() and len(cedula) == 10:
                        if Persona.objects.filter(cedula=cedula, status=True).exists():
                            existe = True
                            persona = Persona.objects.get(cedula=cedula, status=True)

                        if Trabajador.objects.filter(persona__cedula=cedula, persona__status=True, status=True).exists():
                            return JsonResponse({'result': False, 'mensaje': u'Ya se encuentra registrado este trabajador.', 'detalle':''})

                        celular = form.cleaned_data['celular']
                        if celular:
                            if not celular.isdigit() or len(celular) != 10:
                                return JsonResponse({'result': False, 'mensaje': u'Ha ocurrido un error al ingresar el número de TELÉFONO.', 'detalle': 'Asegúrese que sean 10 dígitos.'})

                        sueldo = form.cleaned_data['sueldo']
                        if sueldo<0:
                             return JsonResponse({'result': False, 'mensaje': u'Ha ocurrido un error al ingresar el de sueldo del trabajador.', 'detalle': 'No puede ingresar un valor menor a 0'})

                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        apellido1 = normalizarTexto(form.cleaned_data['apellido1'])
                        apellido2 = normalizarTexto(form.cleaned_data['apellido2'])
                        direccion = normalizarTexto(form.cleaned_data['direccion'])
                        correo = form.cleaned_data['correo']


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

                        trabajador = Trabajador(
                            persona=persona,
                            sueldo=sueldo,
                        )
                        trabajador.save()
                        return JsonResponse({'result': True, 'mensaje':u'El trabajador ha sido registrado en el sistema excitosamente.'})
                    else:
                        return JsonResponse({'result': False, 'mensaje': u'Ingrese una cédula válida.','detalle': ''})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con el registro del trabajador.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = TrabajadorForm(request.POST)
                if form.is_valid():
                    trabajador = Trabajador.objects.get(id=request.POST['id'])
                    cedula = form.cleaned_data['cedula']
                    if cedula.isdigit() and len(cedula) == 10:
                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        apellido1 = normalizarTexto(form.cleaned_data['apellido1'])
                        apellido2 = normalizarTexto(form.cleaned_data['apellido2'])
                        direccion = normalizarTexto(form.cleaned_data['direccion'])
                        sueldo = form.cleaned_data['sueldo']
                        correo = form.cleaned_data['correo']
                        celular = form.cleaned_data.get('celular')

                        existe = False
                        persona = None

                        if Persona.objects.filter(cedula=cedula, status=True).exists():
                            existe = True
                            persona = Persona.objects.get(cedula=cedula, status=True)

                        if Trabajador.objects.filter(persona__cedula=cedula, persona__status=True, status=True).exclude(persona__cedula=trabajador.persona.cedula).exists():
                            return JsonResponse({'result': False, 'mensaje': u'Ya se encuentra registrado un trabajador con esta cédula.', 'detalle':''})

                        if celular:
                            if not celular.isdigit() or len(celular) != 10:
                                return JsonResponse({'result': False, 'mensaje': u'Ha ocurrido un error al ingresar el número de TELÉFONO.', 'detalle': 'Asegúrese que sean 10 dígitos.'})

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
                            trabajador.persona = persona
                            trabajador.sueldo = sueldo
                            trabajador.save()
                            return JsonResponse({'result': True, 'mensaje': u'Se modificado los datos del cliente excitosamente.'})

                        persona.cedula = cedula
                        persona.nombre = nombre
                        persona.apellido1 = apellido1
                        persona.apellido2 = apellido2
                        persona.direccion = direccion
                        persona.celular = celular
                        persona.correo = correo
                        trabajador.sueldo = sueldo
                        persona.save()
                        trabajador.save()
                        return JsonResponse({'result': True, 'mensaje':u'Se modificado los datos del trabajador excitosamente.'})
                    else:
                        return JsonResponse({'result': False, 'mensaje': u'Ingrese una cédula válida.','detalle': ''})
                else:
                    return JsonResponse({'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': False, 'mensaje':u'Parece que ha ocurrido un error con la modificación de los datos del cliente.', 'detalle': str(ex)})


        if action == 'del':
            try:
                trabajador = Trabajador.objects.get(pk=request.POST['id'])
                persona = Persona.objects.get(id=trabajador.persona_id)

                if not persona.personacliente.filter(status=True).exists():
                    persona.status = False
                    persona.save()

                trabajador.status = False
                trabajador.save()
                return JsonResponse({'result': True, 'mensaje': 'Se ha eliminado el trabajador excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})


    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'add':
                try:
                    form = TrabajadorForm()
                    template = get_template('modals/form_persona.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})

            if action == 'edit':
                try:
                    trabajador = Trabajador.objects.get(pk=request.GET['id'])
                    form = TrabajadorForm(initial={'nombre': trabajador.persona.nombre, 'apellido1': trabajador.persona.apellido1, 'apellido2': trabajador.persona.apellido2,
                                                'cedula': trabajador.persona.cedula, 'correo': trabajador.persona.correo, 'direccion': trabajador.persona.direccion,
                                                'celular': trabajador.persona.celular, 'sueldo': trabajador.sueldo})
                    template = get_template('modals/form_persona.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})

            if action == 'obtenercliente':
                try:
                    return obtenerPersonaCedula(request.GET['cedula'], data)
                except Exception as ex:
                    return JsonResponse({'result': False})

        else:
            try:
                data['title'] = u'Administración de Trabajadores'
                data['subtitle'] = u'Administre sus trabajadores'
                data['administracion'] = True
                data['adm_activo'] = 2
                data['list'] = Trabajador.objects.filter(persona__status=True, status=True)

                return render(request, 'administracion/adm_trabajadores.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado, {str(ex)}")
