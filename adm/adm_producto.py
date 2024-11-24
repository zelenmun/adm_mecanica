from pickletools import decimalnl_long

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import transaction

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, AumentarProductoForm
from core.funciones import normalizarTexto
from django.template.loader import get_template

# IMPORTACIONES DE MODELOS
from adm.models import Categoria, Producto, Vitrina, KardexProducto


def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

        if action == 'add':
            try:
                form = ProductoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['nombre'])
                    precio = form.cleaned_data['precio']
                    cantidad = form.cleaned_data['cantidad']
                    vitrina = form.cleaned_data['vitrina']
                    subcategoria = form.cleaned_data['subcategoria']
                    descripcion = normalizarTexto(form.cleaned_data['descripcion'])

                    # VALIDACIÓN: NO SE PERMITEN DOS PRODUCTOS IGUALES
                    if Producto.objects.filter(nombre=nombre, status=True).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Este producto ya consta en el inventario.', 'detalle': ''})

                    # CREACIÓN DEL PRODUCTO
                    producto = Producto(
                        nombre=nombre,
                        precio=precio,
                        vitrina=vitrina,
                        subcategoria=subcategoria,
                        descripcion=descripcion
                    )
                    producto.save()

                    # CREACIÓN DEL HISTORIAL KARDEX
                    kardex = KardexProducto(
                        producto=producto,
                        tipo_movimiento=1,
                        cantidad=cantidad,
                        costo_unitario=precio
                    )
                    kardex.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado el producto excitosamente'})
                return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente.', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'adicionar':
            try:
                form = AumentarProductoForm(request.POST)
                if form.is_valid():
                    precio = form.cleaned_data['precio']
                    cantidad = form.cleaned_data['cantidad']

                    producto = Producto.objects.get(pk=request.POST['id'])

                    if 'precio' in form.cleaned_data and precio is not None:
                        producto.precio = precio

                    producto.save()

                    # CREACIÓN DEL HISTORIAL KARDEX
                    kardex = KardexProducto(
                        producto=producto,
                        tipo_movimiento=1,
                        cantidad=cantidad,
                        costo_unitario=producto.precio
                    )
                    kardex.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado el producto excitosamente'})
                return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente.', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'add':
                try:
                    form = ProductoForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'adicionar':
                try:
                    form = AumentarProductoForm()
                    template = get_template('modals/form.html')
                    return JsonResponse({'result': True, 'data': template.render({'form': form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'kardex':
                try:
                    producto = Producto.objects.get(pk=request.GET['id'])
                    data['title'] = f'Kardex del producto: {producto.nombre}'
                    data['subtitle'] = f'Visualice los movimientos de su producto: {producto.nombre}'
                    data['list'] = KardexProducto.objects.filter(status=True, producto=producto)
                    return render(request, 'administracion/adm_productos_kardex.html', data)
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

        else:
            try:
                data['title'] = u'Administración de Productos'
                data['subtitle'] = u'Administre sus productos'
                data['list'] = Producto.objects.filter(status=True)
                return render(request, 'administracion/adm_productos.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
