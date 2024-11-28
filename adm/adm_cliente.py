from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from adm.models import Cliente
from adm.forms import ClienteForm
from django.template.loader import get_template
from core.funciones import normalizarTexto
from core.models import Persona


# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'add':
            try:
                form = ClienteForm(request.POST)
                if form.is_valid():
                    cedula = form.cleaned_data['cedula']
                    nombre = form.cleaned_data['nombre']
                    apellido1 = form.cleaned_data['apellido1']
                    apellido2 = form.cleaned_data.get('apellido2')
                    direccion = form.cleaned_data.get('direccion')
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
                return JsonResponse( {'result': False, 'mensaje': u'No se ha llenado correctamente el formulario.','detalle': ''})
            except Exception as ex:
                return JsonResponse({'result': True, 'mensaje':u'Parece que ha ocurrido un error con el registro del cliente.', 'detalle': str(ex)})


    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action== 'add':
                try:
                    form = ClienteForm() #el formulario para registrar clientes
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.','detalle': str(ex)})
        else:
            try:
                data['title'] = u'Administración de Clientes'
                data['subtitle'] = u'Administre sus clientes'
                data['list'] = Cliente.objects.filter(persona__status=True, status=True).select_related('persona').order_by('-id')
                return render(request, 'administracion/adm_clientes.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
