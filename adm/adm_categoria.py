from core.funciones import normalizarTexto

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

# IMPORTACIONES DE FORMULARIOS
from core.forms import PersonaForm
from adm.forms import TextoForm, SubcategoriaForm

# IMPORTACIONES DE MODELOS
from core.models import Persona
from adm.models import Categoria, Subcategoria

def view(request):
    data = {}
    if request.method == 'POST':
        data['action'] = action = request.POST['action']
        if action == 'addcategoria':
            try:
                form = TextoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['texto'])
                    if Categoria.objects.filter(nombre=nombre, status=True).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Ya existe una categoría con ese nombre.', 'detalle':''})
                    categoria = Categoria(nombre=nombre)
                    categoria.save(request)
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado la categoría excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'editcategoria':
            try:
                form = TextoForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['texto'])

                    categoria = Categoria.objects.get(pk=request.POST['id'])

                    if Categoria.objects.filter(nombre=nombre, status=True).exists():
                        return JsonResponse({"result": False, 'mensaje': u'Ya existe una categoría con ese nombre.', 'detalle':''})
                    if categoria.subcategoria.filter(status=True).exists():
                        return JsonResponse({"result": False, 'mensaje': u'No puedes modificar una categoría que tiene subcategorías.', 'detalle':''})

                    categoria.nombre = nombre
                    categoria.save()
                    return JsonResponse({'result': True, 'mensaje': 'Se ha editado la categoría excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'delcategoria':
            try:
                categoria = Categoria.objects.get(pk=request.POST['id'])
                if categoria.subcategoria.exists():
                    return JsonResponse({"result": False, 'mensaje': u'No puedes eliminar una categoría que tiene subcategorías.', 'detalle': ''})
                categoria.status = False
                categoria.save()
                return JsonResponse({'result': True, 'mensaje': 'Se ha eliminado la categoría excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'addsubcategoria':
            try:
                form = SubcategoriaForm(request.POST)
                if form.is_valid():
                    subcategoria = normalizarTexto(form.cleaned_data['subcategoria'])
                    categoria = form.cleaned_data['categoria']

                    if Subcategoria.objects.filter(nombre=subcategoria, categoria=categoria).exists():
                        return JsonResponse({'result': False, 'mensaje': 'Ya existe una subcategoría con ese nombre en esta categoría.', 'detalle': ''})

                    subcategoria = Subcategoria(nombre=subcategoria, categoria=categoria)
                    subcategoria.save(request)
                    return JsonResponse({'result': True, 'mensaje': 'Se ha guardado la categoría excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle':''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'editsubcategoria':
            try:
                form = SubcategoriaForm(request.POST)
                if form.is_valid():
                    nombre = normalizarTexto(form.cleaned_data['subcategoria'])
                    categoria = form.cleaned_data['categoria']

                    subcategoria = Subcategoria.objects.get(pk=request.POST['id'])

                    if Subcategoria.objects.filter(nombre=nombre, categoria=categoria, status=True).exclude(pk=subcategoria.id).exists():
                        return JsonResponse({'result': False, 'mensaje': 'Ya existe otra subcategoría con ese nombre en esta categoría.', 'detalle':''})

                    subcategoria.nombre = nombre
                    subcategoria.categoria = categoria

                    subcategoria.save(request)
                    return JsonResponse({'result': True, 'mensaje': 'Se ha editado la categoría excitosamente'})
                else:
                    return JsonResponse({"result": False, 'mensaje': u'El formulario no es válido.', 'detalle': ''})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})

        if action == 'delsubcategoria':
            try:
                subcategoria = Subcategoria.objects.get(pk=request.POST['id'])
                subcategoria.status = False
                subcategoria.save()
                return JsonResponse({'result': True, 'mensaje': 'Se ha eliminado la subcategoría excitosamente'})
            except Exception as ex:
                return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al guardar los datos.', 'detalle': str(ex)})



        return JsonResponse({"result": False, 'mensaje': u'Alguna pendejada habrán hecho.'})
    else:
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'addcategoria':
                try:
                    form = TextoForm()
                    form.fields['texto'].widget.attrs['placeholder'] = 'Nombre de la categoria'
                    form.fields['texto'].label = u'Nombre'
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'addsubcategoria':
                try:
                    form = SubcategoriaForm()
                    form.fields['subcategoria'].widget.attrs['placeholder'] = 'Nombre de la Subcategoria'
                    form.fields['subcategoria'].label = u'Subcategoria'
                    form.fields['categoria'].label = u'Categoria'
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'editcategoria':
                try:
                    categoria = Categoria.objects.get(pk=request.GET['id'])
                    form = TextoForm(initial={'texto': categoria.nombre})

                    form.fields['texto'].widget.attrs['placeholder'] = 'Nombre de la categoria'
                    form.fields['texto'].label = u'Nombre'

                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})

            if action == 'editsubcategoria':
                try:
                    subcategoria = Subcategoria.objects.get(pk=request.GET['id'])
                    form = SubcategoriaForm(initial={'subcategoria': subcategoria.nombre, 'categoria': subcategoria.categoria})
                    form.fields['subcategoria'].widget.attrs['placeholder'] = 'Nombre de la Subcategoria'
                    form.fields['subcategoria'].label = u'Subcategoria'
                    form.fields['categoria'].label = u'Categoria'
                    template = get_template('modals/form.html')
                    return JsonResponse({'result':True, 'data':template.render({'form':form})})
                except Exception as ex:
                    return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})
        else:
            try:
                data['title'] = u'Administración de Categorías y Subcategorías'
                data['subtitle'] = u'Administre las categorías y subcategorías de los productos'
                data['list1'] = Categoria.objects.filter(status=True).order_by('-id')
                data['list2'] = Subcategoria.objects.filter(status=True).order_by('-id')
                data['administracion'] = True
                data['adm_activo'] = 3
                return render(request, 'administracion/adm_categorias.html', data)
            except Exception as ex:
                data['title'] = u'Error en: Categorías'
                data['subtitle'] = u''
                data['exception'] = str(ex)
                data['dashboardatras'] = True
                return render(request, 'exceptions/5XX.html', data)