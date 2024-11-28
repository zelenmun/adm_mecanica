from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum

from adm.models import TrabajoDia
from datetime import datetime
def view(request):
    data = {}
    hoy = datetime.now().date()  # Obtiene solo la fecha (sin hora)
    data['hoy'] = hoy
    if request.method == 'POST':
        action = request.POST['action']
    else:
        if 'action' in request.GET:
            action = request.GET['action']
        else:
            try:
                data['buscador'] = True
                data['title'] = f'Dashboard Mecánica | {hoy}'
                data['dias'] = u'7'
                data['cantidad'] = u'200.00'
                workday = TrabajoDia.objects.filter(status=True, fecha_creacion__date=hoy)
                precio_total = workday.aggregate(Sum('precio'))['precio__sum']
                if precio_total is None:
                    precio_total = 0
                data['servicios'] = f'{precio_total}'
                data['dashboardatras'] = True
                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
