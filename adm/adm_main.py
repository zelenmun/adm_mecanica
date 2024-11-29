from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum

from adm.models import TrabajoDia
from datetime import datetime, timedelta, date
def view(request):
    data = {}
    hoy = datetime.now().date()  # Obtiene solo la fecha (sin hora)
    data['hoy'] = hoy
    lunes = obtener_rango_semana_actual()
    if request.method == 'POST':
        action = request.POST['action']
    else:
        if 'action' in request.GET:
            action = request.GET['action']
        else:
            try:
                data['buscador'] = True
                data['title'] = f'Dashboard Mecánica | {hoy}'
                data['lunes'] = lunes
                data['cantidad'] = u'200.00'
                workday = TrabajoDia.objects.filter(status=True, fecha_creacion__date=hoy)
                precio_total = 0
                if workday is not None:
                    for day in workday:
                        precio_total += day.preciot

                if precio_total is None:
                    precio_total = 0

                data['servicios'] = f'{precio_total}'
                data['dashboardatras'] = True
                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado {str(ex)}")


def obtener_rango_semana_actual():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes