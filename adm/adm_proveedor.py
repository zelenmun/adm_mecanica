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
                data['title'] = u'Administración de Proveedores'
                data['subtitle'] = u'Administre sus proveedores'
                return render(request, 'administracion/adm_proveedores.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado, {str(ex)}")
