from django import forms
from django.contrib.admin.widgets import AutocompleteSelect
from core.models import Persona
from core.modeloform import FormModeloBase
from .models import Trabajo, Trabajador, Cliente, Categoria, Vitrina, Subcategoria, Producto

class AddTrabajoForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Trabajo.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    precio = forms.CharField(label=u'Precio Registrado', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))
    nprecio = forms.DecimalField(label=u'Precio Personalizado', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'12', 'separator': 'true',"separatortitle":'Opcional'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))

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

class TrabajoForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Nombre del Trabajo'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Trabajo'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))


class MultipleServiceForm(FormModeloBase):
    producto = forms.ModelChoiceField(label=u'Producto', queryset=Producto.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    descuento = forms.DecimalField(label=u'Descuento ($)', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Descuento General'}))
    preciou = forms.CharField(label=u'Precio Unitario ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Precio Unitario', 'separator': 'true',"separatortitle":'Detalle de la venta'}))
    cantidad = forms.IntegerField(label=u'Cantidad', required=True, widget=forms.NumberInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Cantidad'}))
    precios = forms.CharField(label=u'Total ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Total'}))
    preciot = forms.CharField(label=u'Total Venta ($$)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Precio Total Venta'}))
