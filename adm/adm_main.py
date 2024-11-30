from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum

from adm.models import TrabajoDia, Venta, VentaDetalle
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

            if action == 'cargarchartarea':
                try:
                    valores = [130, 391, 492, 290, 930, 817, 245]

                    return JsonResponse({'valores': valores})
                except Exception as ex:
                    return JsonResponse({'valores': [0]})
        else:
            try:
                data['buscador'] = True
                data['title'] = f'Dashboard Mecánica | {hoy}'
                data['lunes'] = lunes
                data['cantidad'] = u'200.00'

                totalservicios = calcular_total_servicios(hoy)
                totalventas = calcular_total_ventas(hoy)

                totalingreso = totalservicios + totalventas

                data['totalservicios'] = f'{totalservicios}'
                data['totalventas'] = f'{totalventas}'
                data['totalingreso'] = f'{totalingreso}'
                data['dashboardatras'] = True
                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado {str(ex)}")

def calcular_total_servicios(hoy):
    """
    Calcula el precio total de los trabajos del día con estado True.
    """
    try:
        resultado = TrabajoDia.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('preciot'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_ventas(hoy):
    """
    Calcula el precio total de las ventas del día con estado True.
    """
    try:
        resultado = Venta.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('preciov'))
        return resultado['total'] or 0
    except Exception as ex:
        return 0

def obtener_rango_semana_actual():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes