from django.shortcuts import render
from django.http import HttpResponse
def view(request):
    data = {}
    if request.method == 'POST':
        action = request.POST['action']
    else:
        if 'action' in request.GET:
            action = request.GET['action']
        else:
            try:
                data['buscador'] = True
                data['title'] = u'Dashboard Mecánica'
                data['dias'] = u'7'
                data['cantidad'] = u'200.00'
                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
