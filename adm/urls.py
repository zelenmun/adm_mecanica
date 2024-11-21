# adm/urls.py
from django.urls import re_path
from . import adm_main, adm_servicio

urlpatterns = [
    re_path(r'^$', adm_main.view, name='adm_main'),
    re_path(r'^serviciosmecanica$', adm_servicio.view, name='adm_servicio'),
]
