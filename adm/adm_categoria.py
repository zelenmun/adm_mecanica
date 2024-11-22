from django.http import HttpResponse
from django.shortcuts import render

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
        else:
            try:
                data['title'] = u'Administración de Categorías'
                data['subtitle'] = u'Administre las categorías de los productos'
                return render(request, 'administracion/adm_categorias.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
