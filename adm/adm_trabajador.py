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
                data['title'] = u'Administración de Trabajadores'
                data['subtitle'] = u'Administre sus trabajadores'
                data['administracion'] = True
                data['adm_activo'] = 2
                return render(request, 'administracion/adm_trabajadores.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
