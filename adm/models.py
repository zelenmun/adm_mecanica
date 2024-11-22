from django.db import models

from core.models import ModeloBase, Persona


# Create your models here.
class Vehiculo(ModeloBase):
    descripcion = models.CharField(max_length=2000, blank=True, null=True, verbose_name=u'Descripción del vehículo')
    placa = models.CharField(max_length=10, blank=True, null=True, verbose_name=u'Placa del vehículo')
    modelo = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Modelo del vehículo')
    marca = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Marca del vehículo')

class Cliente(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name=u'Persona', related_name='clientes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name=u'Vehículo', related_name='clientes_asociados')

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