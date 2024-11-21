# adm/urls.py
from django.urls import re_path
from . import adm_main, adm_registrousuario

urlpatterns = [
    re_path(r'^$', adm_main.view, name='adm_main'),
]
