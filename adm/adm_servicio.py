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
    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'add':
                try:
                    form = AddTrabajoForm()
                    data['form'] = form
                    data['action'] = action
                    template = get_template("adm_servicios/modal/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    pass
        else:
            try:
                data['title'] = u'Servicios de Mecánica'
                return render(request, 'adm_servicios/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
