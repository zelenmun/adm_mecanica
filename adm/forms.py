from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from core.models import Persona
from core.modeloform import FormModeloBase
from .models import Trabajo, Trabajador, Cliente, Categoria, Vitrina, Subcategoria, Producto

class AddTrabajoForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Producto.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'12'}))

class TextoForm(FormModeloBase):
    texto = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))

class SubcategoriaForm(FormModeloBase):
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    subcategoria = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))

class ProductoForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder': 'Nombre del Producto'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Producto'}))
    cantidad = forms.IntegerField(label=u'Cantidad', required=True, widget=forms.NumberInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cantidad de Productos ingresados'}))
    vitrina = forms.ModelChoiceField(label=u'Vitrina', queryset=Vitrina.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control', 'separator': 'true',"separatortitle":'Detalle del producto'}))
    subcategoria = forms.ModelChoiceField(label=u'Subcategoria', queryset=Subcategoria.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    descripcion = forms.CharField(label=u'Descripción', max_length=2000, required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Descripcion del Producto', 'class': 'form-control'}))

class AumentarProductoForm(FormModeloBase):
    cantidad = forms.IntegerField(label=u'Cantidad', required=True, widget=forms.NumberInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cantidad a aumentar'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Producto'}))
