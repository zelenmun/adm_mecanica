from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum

from adm.models import (KardexProducto, vVenta, VentaProductoDetalle, VentaAdicionalDetalle, VentaServicioDetalle,
                        GastoNoOperativo)
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

                totalservicios = calcular_total_servicios(hoy)
                totalrepuestos = calcular_total_repuestos(hoy)
                totaldetalles = calcular_total_detalles(hoy)
                totalegresos = calcular_total_egreso(lunes)

                totalingreso = (totalservicios + totalrepuestos + totaldetalles) - totalegresos

                data['totalservicios'] = f'{totalservicios}'
                data['totalrepuestos'] = f'{totalrepuestos}'

                data['balancegeneral'] = f'{totalingreso}'
                data['totalegresos'] = f'{totalegresos}'
                data['dashboardatras'] = True

                ventasdia = vVenta.objects.filter(status=True, fecha_venta__date=hoy)
                data['list'] = ventasdia

                return render(request, 'dashboard/view.html', data)
            except Exception as ex:
                return HttpResponse(f"Método no soportado {str(ex)}")

def calcular_total_servicios(hoy):
    """
    Calcula el precio total de los trabajos del día con estado True.
    """
    try:
        resultado = VentaServicioDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('total'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_repuestos(hoy):
    """
    Calcula el precio total de los repuestos vendidos del día con estado True.
    """
    try:
        resultado = VentaProductoDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('total'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_detalles(hoy):
    """
    Calcula el precio total de los repuestos vendidos del día con estado True.
    """
    try:
        resultado = VentaAdicionalDetalle.objects.filter(status=True, fecha_creacion__date=hoy).aggregate(total=Sum('precio'))
        return resultado['total'] or 0
    except Exception as e:
        return 0

def calcular_total_egreso(lunes):
    """
    Calcula el precio total de los repuestos vendidos del día con estado True.
    """
    try:
        resultado = KardexProducto.objects.filter(status=True, tipo_movimiento=1,fecha_creacion__gte=lunes).aggregate(total=Sum('costo_total'))
        resultado2 = GastoNoOperativo.objects.filter(status=True, fecha_creacion__gte=lunes).aggregate(total=Sum('valor'))

        valor1 = 0
        valor2 = 0
        if resultado['total']:
            valor1 = resultado['total']
        if resultado2['total']:
            valor2 = resultado2['total']
        return valor1 + valor2
    except Exception as e:
        return 0


def obtener_rango_semana_actual():
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    return lunes