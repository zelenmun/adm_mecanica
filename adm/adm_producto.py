from pickletools import decimalnl_long
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import transaction

# IMPORTACIONES DE FORMULARIOS
from adm.forms import ProductoForm, AumentarProductoForm
from core.funciones import normalizarTexto
from django.template.loader import get_template

# IMPORTACIONES DE MODELOS
from adm.models import Categoria, Producto, Vitrina, KardexProducto, LoteProducto

@transaction.atomic
def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']

        if action == 'add':
            try:
                with transaction.atomic():
                    form = ProductoForm(request.POST)
                    if form.is_valid():
                        nombre = normalizarTexto(form.cleaned_data['nombre'])
                        preciocompra = form.cleaned_data['preciocompra']
                        precioventa = form.cleaned_data['precioventa']
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
                            vitrina=vitrina,
                            subcategoria=subcategoria,
                            descripcion=descripcion
                        )
                        producto.save()

                        lote = LoteProducto(
                            producto=producto,
                            cantidad=cantidad,
                            precioventa=precioventa,
                            preciocompra=preciocompra,
                            fecha_adquisicion=datetime.now()
                        )
                        lote.save()

                        # CREACIÓN DEL HISTORIAL KARDEX
                        kardex = KardexProducto(
                            producto=producto,
                            tipo_movimiento=1,
                            cantidad=cantidad,
                            costo_unitario=lote.preciocompra,
                            lote=lote,
                            precio_unitario=lote.precioventa
                        )
                        kardex.save()

                        return JsonResponse({'result': True, 'mensaje': 'Se ha guardado el producto excitosamente'})
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no se ha llenado correctamente.', 'detalle': ''})
            except Exception as ex:
                transaction.set_rollback(True)
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'edit':
            try:
                form = ProductoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['nombre'])
                    vitrina = form.cleaned_data['vitrina']
                    subcategoria = form.cleaned_data['subcategoria']
                    descripcion = normalizarTexto(form.cleaned_data['descripcion'])

                    producto = Producto.objects.get(id=request.POST['id'])

                    if Producto.objects.filter(nombre=nombre, status=True).exclude(pk=producto.id).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Este producto ya consta en el inventario.', 'detalle': ''})

                    producto.nombre = nombre
                    producto.vitrina = vitrina
                    producto.subcategoria = subcategoria
                    producto.descripcion = descripcion
                    producto.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha editado la categoría excitosamente'})
                return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'del':
            try:
                producto = Producto.objects.get(id=request.POST['id'])
                producto.status = False
                producto.save()
                return JsonResponse({'result': True, 'mensaje': 'Se ha eliminado el producto excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al eliminar el producto.', 'detalle': str(ex)})

        if action == 'adicionar':
            try:
                form = AumentarProductoForm(request.POST)
                if form.is_valid():
                    preciocompra = form.cleaned_data['preciocompra']
                    precioventa = form.cleaned_data['precioventa']
                    cantidad = form.cleaned_data['cantidad']

                    producto = Producto.objects.get(pk=request.POST['id'])
                    lot = LoteProducto.objects.filter(producto=producto).order_by('-id').first()

                    if preciocompra is None:
                        preciocompra = lot.preciocompra
                    if precioventa is None:
                        precioventa = lot.precioventa
                    # CREACIÓN DEL LOTE
                    lote = LoteProducto(
                        producto=producto,
                        cantidad=cantidad,
                        preciocompra=preciocompra,
                        precioventa=precioventa,
                        fecha_adquisicion=datetime.now()
                    )
                    lote.save()

                    # CREACIÓN DEL HISTORIAL KARDEX
                    kardex = KardexProducto(
                        producto=producto,
                        tipo_movimiento=1,
                        cantidad=cantidad,
                        costo_unitario=lote.preciocompra,
                        lote=lote,
                        precio_unitario=lote.precioventa
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

            if action == 'edit':
                try:
                    producto = Producto.objects.get(pk=request.GET['id'])
                    form = ProductoForm(initial={
                        'nombre':producto.nombre,
                        'precioventa':producto.precioventa,
                        'preciocompra':producto.preciocompra,
                        'cantidad':producto.get_cantidad_actual(),
                        'vitrina':producto.vitrina,
                        'subcategoria':producto.subcategoria,
                        'descripcion':producto.descripcion})
                    # form.fields['cantidad'].widget.attrs['readonly'] = True
                    # form.fields['preciocompra'].widget.attrs['readonly'] = True
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
                data['list'] = Producto.objects.filter(status=True).order_by('-id')
                data['activo'] = 3
                return render(request, 'administracion/adm_productos.html', data)
            except Exception as ex:
                return HttpResponse("Método no soportado")
