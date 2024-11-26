from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

from core.funciones import normalizarTexto

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm
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
                data['title'] = u''
                data['subtitle'] = u''
                return render(request, '', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
