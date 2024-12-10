from email.policy import default

from django import forms
from django.db.models import Exists, OuterRef
from django.contrib.admin.widgets import AutocompleteSelect
from core.models import Persona
from core.modeloform import FormModeloBase
from .models import Trabajo, Trabajador, Cliente, Categoria, Vitrina, Subcategoria, Producto, LoteProducto

class AddTrabajoForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Trabajo.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    precio = forms.CharField(label=u'Precio Registrado', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))
    nprecio = forms.DecimalField(label=u'Precio Personalizado', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'12', 'separator': 'true',"separatortitle":'Opcional'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))

class TrabajoDiaForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Trabajo.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Trabajo'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))

class TextoForm(FormModeloBase):
    texto = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))

class DecimalForm(FormModeloBase):
    decimal = forms.DecimalField(max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'12'}))

class SubcategoriaForm(FormModeloBase):
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    subcategoria = forms.CharField(max_length=500, required=True, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))

class ProductoForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Nombre del Producto'}))
    cantidad = forms.IntegerField(label=u'Cantidad', required=True, widget=forms.NumberInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cantidad de Productos ingresados'}))
    preciocompra = forms.DecimalField(label=u'Precio Compra (unidad)', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Producto'}))
    precioventa = forms.DecimalField(label=u'Precio Venta (unidad)', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Producto'}))
    vitrina = forms.ModelChoiceField(label=u'Vitrina', queryset=Vitrina.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control', 'separator': 'true',"separatortitle":'Detalle del producto'}))
    subcategoria = forms.ModelChoiceField(label=u'Subcategoria', queryset=Subcategoria.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    descripcion = forms.CharField(label=u'Descripción', max_length=2000, required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Descripcion del Producto', 'class': 'form-control'}))

class AumentarProductoForm(FormModeloBase):
    cantidad = forms.IntegerField(label=u'Cantidad', required=True, widget=forms.NumberInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cantidad a aumentar'}))
    preciocompra = forms.DecimalField(label=u'Precio Compra', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio de Compra'}))
    precioventa = forms.DecimalField(label=u'Precio Venta', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio de Venta'}))

class TrabajoForm(FormModeloBase):
    nombre = forms.CharField(label=u'Nombre', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Nombre del Trabajo'}))
    precio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=True, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'6', 'placeholder': 'Precio del Trabajo'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))

class ClienteForm(FormModeloBase):
    cedula = forms.CharField(label=u'Cédula', max_length=10, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cédula de Identidad'}))
    nombre = forms.CharField(label=u'Nombres', max_length=200, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Nombres'}))
    apellido1 = forms.CharField(label=u'Primer Apellido', max_length=200, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Apellido Paterno'}))
    apellido2 = forms.CharField(label=u'Segundo Apellido', max_length=200, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Apellido Materno'}))
    direccion = forms.CharField(label=u'Dirección', max_length=200, required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control', 'placeholder': 'Dirección de domicilio'}))
    celular = forms.CharField(label=u'Teléfono ', max_length=10, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Número de Teléfono'}))
    correo = forms.CharField(label=u'Correo Electrónico', max_length=200, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Email'}))

class AddVentaForm(FormModeloBase):
    producto = forms.ModelChoiceField(label=u'Producto', queryset=Producto.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    precio = forms.CharField(label=u'Precio Registrado', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '12', 'class': 'form-control'}))
    cantidad = forms.IntegerField(label=u'Cantidad', initial=1, required=True, widget=forms.NumberInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Cantidad vendida'}))
    cliente = forms.ModelChoiceField(label=u'Cliente', queryset=Cliente.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    nprecio = forms.DecimalField(label=u'Precio Personalizado', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '12', 'separator': 'true', "separatortitle": 'Opcional'}))
    trabajador = forms.ModelChoiceField(label=u'Trabajador', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '12', 'class': 'form-control'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '3', 'placeholder': 'Detalle del Trabajo', 'class': 'form-control'}))

class RegistroVentaForm(FormModeloBase):
    producto = forms.ModelChoiceField(label=u'Producto', queryset=Producto.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '4', 'class': 'form-control'}))
    lote = forms.ModelChoiceField(label=u'Producto Lote', queryset=LoteProducto.objects.none(), required=True, widget=forms.Select(attrs={'col': '4', 'class': 'form-control'}))
    cantidad = forms.IntegerField(label=u'Cantidad (N°)', min_value=1, required=True, widget=forms.NumberInput(attrs={'col': '4', 'class': 'form-control', 'placeholder': 'Cantidad'}))
    abono = forms.DecimalField(label=u'Abono ($)', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '4', 'separator': 'true',"separatortitle":'Detalle general de la venta', 'placeholder': 'Pago del Cliente'}))
    descuento = forms.DecimalField(label=u'Descuento ($)', min_value=0,max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'4', 'placeholder': 'Descuento de la Venta'}))
    detalle = forms.CharField(label=u'Comentarios', required=False, widget=forms.Textarea(attrs={'rows': '1', 'placeholder': 'Información Adicional...', 'class': 'form-control', 'col':'4'}))

class RegistroTotalForm(FormModeloBase):
    preciou = forms.CharField(label=u'Precio Unitario ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Precio Unitario'}))
    precios = forms.CharField(label=u'Total Producto ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Total Producto'}))
    preciosd = forms.CharField(label=u'Subtotal ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Precio Total Venta', 'separator': 'true',"separatortitle":'Detalle general de la venta'}))
    preciot = forms.CharField(label=u'Total Venta ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Precio Total Venta'}))

class RegistroServicioForm(FormModeloBase):
    trabajo = forms.ModelChoiceField(label=u'Trabajo', queryset=Trabajo.objects.filter(status=True), required=True, widget=forms.Select(attrs={'col': '4', 'class': 'form-control'}))
    cantidad = forms.IntegerField(label=u'Cantidad', min_value=1, required=True, widget=forms.NumberInput(attrs={'col': '4', 'class': 'form-control', 'placeholder': 'Cantidad'}))
    trabajador = forms.ModelChoiceField(label=u'Mecánico', queryset=Trabajador.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '4', 'class': 'form-control'}))
    # preciou = forms.CharField(label=u'Precio Unitario ($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '4', 'class': 'form-control', 'placeholder': 'Precio Unitario', 'separator': 'true',"separatortitle":'Detalle del servicio'}))
    # precios = forms.CharField(label=u'Total Producto($)', max_length=500, required=False, widget=forms.TextInput(attrs={'col': '4', 'class': 'form-control', 'placeholder': 'Total'}))
    abono = forms.DecimalField(label=u'Abono ($)', min_value=0, max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '4', 'separator': 'true',"separatortitle":'Detalle general de la venta', 'placeholder': 'Pago del Cliente'}))
    descuento = forms.DecimalField(label=u'Descuento ($)', min_value=0,max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col':'4', 'placeholder': 'Descuento de la Venta'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '1', 'placeholder': 'Información Adicional', 'class': 'form-control', 'col': '4'}))

class GastoNoOperativoForm(FormModeloBase):
    titulo = forms.CharField(label=u'Titulo', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Nombra el Gasto'}))
    valor = forms.CharField(label=u'Valor del gasto ($)', max_length=500, required=True, widget=forms.TextInput(attrs={'col': '6', 'class': 'form-control', 'placeholder': 'Precio del Gasto'}))
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '1', 'placeholder': 'Detalle del Gasto...', 'class': 'form-control', 'col': '12'}))

class VentaProductoForm(FormModeloBase):
    producto = forms.ModelChoiceField(label=u'Producto', queryset=Producto.objects.filter(status=True).filter(Exists(LoteProducto.objects.filter(producto=OuterRef('pk'), cantidad__gt=0))), required=False, widget=forms.Select(attrs={'col': '3', 'class': 'form-control'}))
    lote = forms.ModelChoiceField(label=u'Lote', queryset=LoteProducto.objects.none(), required=False, widget=forms.Select(attrs={'col': '3', 'class': 'form-control'}))
    precioproducto = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '3', 'placeholder': 'Precio'}))
    pcantidad = forms.IntegerField(label=u'Cantidad', min_value=1, required=False, widget=forms.NumberInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Cantidad'}))


class VentaServicioForm(FormModeloBase):
    servicio = forms.ModelChoiceField(label=u'Servicio', queryset=Trabajo.objects.filter(status=True), required=False, widget=forms.Select(attrs={'col': '6', 'class': 'form-control'}))
    precioservicio = forms.DecimalField(label=u'Precio', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '3', 'placeholder': 'Precio'}))
    scantidad = forms.IntegerField(label=u'Cantidad', min_value=1, required=False, widget=forms.NumberInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Cantidad'}))

class VentaAdicionalForm(FormModeloBase):
    detalle = forms.CharField(label=u'Detalle', required=False, widget=forms.Textarea(attrs={'rows': '1', 'placeholder': 'Información Adicional', 'class': 'form-control', 'col': '9'}))
    #compra = forms.DecimalField(label=u'Compra', max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '3', 'placeholder': 'Compra'}))
    ganancia = forms.DecimalField(label=u'Ganancia', min_value=0, max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '3', 'placeholder': 'Ganancia', 'step': '1'}))
    #dcantidad = forms.IntegerField(label=u'Cantidad', min_value=1, required=False, widget=forms.NumberInput(attrs={'col': '3', 'class': 'form-control', 'placeholder': 'Cantidad'}))

class PagoClienteForm(FormModeloBase):
    abono = forms.DecimalField(label=u'Abono', min_value=0, max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '12', 'placeholder': 'Pago del Cliente', 'step': '1'}))
    descuento = forms.DecimalField(label=u'Descuento', min_value=0, max_digits=10, decimal_places=2, required=False, widget=forms.NumberInput(attrs={'decimal': '2', 'col': '12', 'placeholder': 'Descuento de la Venta', 'step': '1'}))



