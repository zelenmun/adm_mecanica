from django import forms
from core.models import Persona
from core.modeloform import FormModeloBase
from .models import *

class AddTrabajoForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Trabajo.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control select2'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=False, widget=forms.TextInput(attrs={'decimal': '2', 'col':'6'}))