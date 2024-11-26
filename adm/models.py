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
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=u'Cliente', related_name='vehiculos')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name=u'Vehículo', related_name='clientes')

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

    def __str__(self):
        return f'{self.codigo}'


class Producto(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre del Producto')
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='productos', blank=True, null=True)
    vitrina = models.ForeignKey(Vitrina, on_delete=models.CASCADE, blank=True, null=True, related_name='producto_vitrina', verbose_name=u'Vitrina')
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Producto')
    descripcion = models.CharField(max_length=2000, blank=True, null=True, verbose_name=u'Descripción del producto')

    def __str__(self):
        return f'{self.nombre} - ${self.precio}'

    def get_cantidad_actual(self):
        """Calcula la cantidad actual desde los movimientos del kardex"""
        entrada = KardexProducto.objects.filter(producto=self, tipo_movimiento=1).aggregate(total=models.Sum('cantidad'))['total'] or 0
        salida = KardexProducto.objects.filter(producto=self, tipo_movimiento=2).aggregate(total=models.Sum('cantidad'))['total'] or 0
        return entrada - salida


TIPO_MOVIMIENTO = (
    (1, u'ENTRADA'),
    (2, u'SALIDA')
)


class KardexProducto(ModeloBase):
    producto = models.ForeignKey(Producto, verbose_name=u'Producto', related_name='kardex_producto', on_delete=models.CASCADE)
    fecha_movimiento = models.DateField(verbose_name=u'Fecha del Movimiento', auto_now_add=True)
    tipo_movimiento = models.IntegerField(default=1, choices=TIPO_MOVIMIENTO, verbose_name=u'Tipo de Movimiento')
    cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=u'Cantidad')
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=u'Costo Unitario')
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=u'Costo Total')
    saldo_cantidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=u'Saldo Cantidad', default=0)
    saldo_costo = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=u'Saldo Costo', default=0)
    observacion = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Observación')

    def __str__(self):
        return f'Kardex de {self.producto.nombre} - {self.fecha_movimiento}'

    def save(self, *args, **kwargs):
        # Cálculo del costo total del movimiento
        self.costo_total = self.cantidad * self.costo_unitario

        # Obtener el último registro del kardex
        ultimo_kardex = KardexProducto.objects.filter(producto=self.producto).order_by('-id').first()

        # Saldo inicial (si no hay registros previos)
        saldo_cantidad_anterior = ultimo_kardex.saldo_cantidad if ultimo_kardex else 0
        saldo_costo_anterior = ultimo_kardex.saldo_costo if ultimo_kardex else 0

        # Ajustar los saldos según el tipo de movimiento
        if self.tipo_movimiento == 1:  # Ingreso
            self.saldo_cantidad = saldo_cantidad_anterior + self.cantidad
            self.saldo_costo = saldo_costo_anterior + self.costo_total
        elif self.tipo_movimiento == 2:  # Egreso
            self.saldo_cantidad = saldo_cantidad_anterior - self.cantidad
            self.saldo_costo = saldo_costo_anterior - self.costo_total

        # Guardar el registro actualizado
        super(KardexProducto, self).save(*args, **kwargs)


class Venta(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Nombre del Cliente')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Nombre del Producto')
    fecha_venta = models.DateField(blank=True, null=True, verbose_name=u'Nombre del Producto')


class Trabajo(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de Trabajo')
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Trabajo')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')

    def __str__(self):
        return f'{self.nombre}'

class TrabajoDia(ModeloBase):
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, verbose_name=u'Trabajo', related_name='trabajo_dia')
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Trabajo')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Nombre del Trabajador', related_name='trabajos_dia')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Nombre del Cliente', related_name='mantenimientos')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')
