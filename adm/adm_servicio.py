from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template
from .forms import AddTrabajoForm

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'add':
            try:
                form = AddTrabajoForm(request.POST)
                if form.is_valid():
                    pass
                return JsonResponse({"result": True, 'mensaje': u'Se ha guardado excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar', 'detalle': str(ex)})
        return HttpResponse("Método no soportado")
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
            return HttpResponse("Método no soportado")
        else:
            try:
                data['title'] = u'Servicios de Mecánica'
                data['subtitle'] = u'Registra los servicios de mecánica realizados'
                return render(request, 'servicios/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
