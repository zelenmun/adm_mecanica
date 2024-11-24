# adm/urls.py
from django.urls import re_path
from . import (adm_main, adm_servicio, adm_cliente, adm_producto, adm_proveedor, adm_trabajador, adm_trabajo, adm_categoria,
               adm_vitrina)

urlpatterns = [
    re_path(r'^$', adm_main.view, name='adm_main'),
    re_path(r'^serviciosmecanica$', adm_servicio.view, name='adm_servicio'),
    re_path(r'^administracion/clientes$', adm_cliente.view, name='clientes'),
    re_path(r'^administracion/proveedores$', adm_proveedor.view, name='proveedores'),
    re_path(r'^administracion/trabajadores$', adm_trabajador.view, name='trabajadores'),
    re_path(r'^administracion/productos$', adm_producto.view, name='productos'),
    re_path(r'^administracion/productos/kardex$', adm_producto.view, name='productos'),
    re_path(r'^administracion/categorias$', adm_categoria.view, name='categorias'),
    re_path(r'^administracion/trabajos$', adm_trabajo.view, name='trabajos'),
    re_path(r'^administracion/vitrinas', adm_vitrina.view, name='vitrinas'),
]
