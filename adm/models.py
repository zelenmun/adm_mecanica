from django.db import models

from core.models import ModeloBase


# Create your models here.
class Cliente(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Cliente')

class Trabajador(ModeloBase):
    nombre = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Nombre del Trabajador')

class Proveedor(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Proveedor')

class Categoria(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de la Categoría')

class Subcategoria(ModeloBase):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True, related_name='subcategoria', verbose_name=u'Nombre de la Categoría')
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de la Subcategoria')

class Estanteria(ModeloBase):
    codigo = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Código de la Estanteria')

class Vehiculo(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, related_name='vehiculo', verbose_name=u'Nombre del Producto')
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Producto')

class Producto(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Producto')
    estanteria = models.ForeignKey(Estanteria, on_delete=models.CASCADE, blank=True, null=True, related_name='producto', verbose_name=u'Nombre del Producto')
    precio = models.DecimalField(default=0, max_digits=30, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Producto')

class Venta(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Nombre del Cliente')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Nombre del Producto')
    fecha_venta = models.DateField(blank=True, null=True, verbose_name=u'Nombre del Producto')

class Trabajo(ModeloBase):
    precio = models.DecimalField(default=0, max_digits=30, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Trabajo')

class Diario(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Producto')
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, blank=True, null=True, related_name='trabajo', verbose_name=u'Nombre del Producto')