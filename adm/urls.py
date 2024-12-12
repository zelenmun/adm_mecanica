# adm/urls.py
from django.urls import re_path
from . import (adm_main, adm_cliente, adm_producto, adm_trabajador, adm_trabajo, adm_categoria,
               adm_vitrina, adm_venta, adm_registroventa, adm_gastonooperativo)

urlpatterns = [
    re_path(r'^$', adm_main.view, name='adm_main'),
    re_path(r'^adm_venta$', adm_venta.view, name='adm_venta'),
    re_path(r'^adm_venta/registroventa$', adm_registroventa.view, name='registroventa'),
    re_path(r'^administracion/clientes$', adm_cliente.view, name='clientes'),
    re_path(r'^administracion/trabajadores$', adm_trabajador.view, name='trabajadores'),
    re_path(r'^administracion/productos$', adm_producto.view, name='productos'),
    re_path(r'^administracion/productos/kardex$', adm_producto.view, name='kardex'),
    re_path(r'^administracion/categorias$', adm_categoria.view, name='categorias'),
    re_path(r'^administracion/trabajos$', adm_trabajo.view, name='trabajos'),
    re_path(r'^administracion/vitrinas', adm_vitrina.view, name='vitrinas'),
    re_path(r'^administracion/gastosnooperativos', adm_gastonooperativo.view, name='gastonooperativo'),
]
