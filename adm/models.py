from django.db import models

from core.models import ModeloBase, Persona


# Create your models here.
class Vehiculo(ModeloBase):
    descripcion = models.CharField(max_length=2000, blank=True, null=True, verbose_name=u'Descripción del vehículo')
    placa = models.CharField(max_length=10, blank=True, null=True, verbose_name=u'Placa del vehículo', unique=True)
    modelo = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Modelo del vehículo')
    marca = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Marca del vehículo')

    def __str__(self):
        return f'{self.modelo} - {self.placa}'

class Cliente(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name=u'Persona', related_name='clientes')
    deuda_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u'Deuda del cliente')

    def __str__(self):
        return f'{self.persona} debe: {self.deuda_pendiente}'

class Vehiculo_Cliente(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=u'Cliente', related_name='cliente_vehiculo')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name=u'Vehículo', related_name='vehiculo_cliente')

    def __str__(self):
        return f'{self.vehiculo} - {self.cliente}'

class Trabajador(ModeloBase):
    nombre = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Nombre del Trabajador')

class Proveedor(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Proveedor')

class Categoria(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de la Categoría')

    def __str__(self):
        return self.nombre

class Subcategoria(ModeloBase):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategoria', verbose_name=u'Nombre de la Categoría')
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de la Subcategoria')

    def __str__(self):
        return f'{self.categoria} - {self.nombre}'

class Vitrina(ModeloBase):
    codigo = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Código de la Vitrina')

class Producto(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Producto')
    estanteria = models.ForeignKey(Vitrina, on_delete=models.CASCADE, blank=True, null=True, related_name='producto', verbose_name=u'Nombre del Producto')
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