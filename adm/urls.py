# adm/urls.py
from django.urls import re_path
from . import adm_main, adm_registrousuario

urlpatterns = [
    re_path(r'^$', adm_main.view, name='adm_main'),
    re_path(r'^signup$', adm_registrousuario.view, name='registrousuario'),
]
