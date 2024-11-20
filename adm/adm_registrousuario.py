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
                form = PersonaForm()
                return render(request, 'adm_signup/view.html', {'form': form})
            except Exception as ex:
                pass
