from django.http import HttpResponse
from django.shortcuts import render

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST['action']
    else:
        if 'action' in request.GET:
            action = request.GET['action']
        else:
            try:
                data['title'] = u'Servicios de Mecánica'
                return render(request, 'adm_servicios/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
