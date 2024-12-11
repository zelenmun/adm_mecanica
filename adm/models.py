from django.db import models
from django.db.models import Model

from core.models import ModeloBase, Persona


# Create your models here.
class Cliente(ModeloBase):
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, verbose_name=u'Persona', related_name='cliente')
    deuda_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name=u'Deuda del cliente')

    def __str__(self):
        return f'<li>{self.persona}</li> <li>DEBE: <b style="color: salmon">${self.deuda_pendiente}</b></li>'

class Trabajador(ModeloBase):
    nombre = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Nombre del Trabajador')
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Sueldo del trabajador')

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
    descripcion = models.CharField(max_length=2000, blank=True, null=True, verbose_name=u'Descripción del producto')

    def __str__(self):
        return f'{self.id} - {self.nombre}'

    def get_cantidad_lote(self, lote_id):
        """Calcula la cantidad actual disponible para un lote específico desde el kardex"""
        entrada = KardexProducto.objects.filter(producto=self, lote_id=lote_id, tipo_movimiento=1).aggregate(total=models.Sum('cantidad'))['total'] or 0

        salida = KardexProducto.objects.filter(producto=self, lote_id=lote_id, tipo_movimiento=2).aggregate(total=models.Sum('cantidad'))['total'] or 0

        return entrada - salida

    def lote_actual(self):
        """Devuelve el lote actual con stock disponible."""
        return LoteProducto.objects.filter(producto=self, cantidad__gt=0).order_by('fecha_adquisicion').first()

class LoteProducto(ModeloBase):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name=u'Producto', related_name='loteproducto')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    precioventa = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio de Venta')
    preciocompra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio de Compra')
    fecha_adquisicion = models.DateTimeField(null=True, blank=True, verbose_name=u'Fecha de ingreso')

    def __str__(self):
        return f"LOTE {self.id} - {self.producto.nombre} - ${self.preciocompra}"

TIPO_MOVIMIENTO = (
    (1, u'ENTRADA'),
    (2, u'SALIDA')
)

class KardexProducto(ModeloBase):
    producto = models.ForeignKey(Producto, verbose_name=u'Producto', related_name='kardex_producto', on_delete=models.CASCADE)
    fecha_movimiento = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha del Movimiento', auto_now_add=True)
    tipo_movimiento = models.IntegerField(blank=True, null=True, default=1, choices=TIPO_MOVIMIENTO, verbose_name=u'Tipo de Movimiento')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    costo_unitario = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, verbose_name=u'Costo Unitario')
    precio_unitario = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=2, verbose_name=u'Precio Unitario')
    costo_total = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2, verbose_name=u'Costo Total')
    saldo_cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Saldo Cantidad')
    saldo_costo = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2, verbose_name=u'Saldo Costo')
    saldo_ganancia = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2, verbose_name=u'Saldo Ganancia')
    observacion = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Observación')
    lote = models.ForeignKey(LoteProducto, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Lote')

    def __str__(self):
        return f'KARDEX DE {self.producto.nombre} - {self.fecha_movimiento}'

    def save(self, *args, **kwargs):
        # Cálculo del costo total del movimiento
        self.costo_total = self.cantidad * self.costo_unitario

        # Si hay precio de venta, calculamos la ganancia
        if self.precio_unitario:
            ganancia_total = (self.precio_unitario - self.costo_unitario) * self.cantidad
        else:
            ganancia_total = 0


        # Obtener el último registro del kardex
        ultimo_kardex = KardexProducto.objects.filter(producto=self.producto).order_by('-id').first()

        # Saldo inicial (si no hay registros previos)
        saldo_cantidad_anterior = ultimo_kardex.saldo_cantidad if ultimo_kardex else 0
        saldo_costo_anterior = ultimo_kardex.saldo_costo if ultimo_kardex else 0

        # Ajustar los saldos según el tipo de movimiento
        if self.tipo_movimiento == 1:  # Ingreso / Compra
            self.saldo_cantidad = saldo_cantidad_anterior + self.cantidad
            self.saldo_costo = saldo_costo_anterior + self.costo_total
            self.saldo_ganancia = 0
        elif self.tipo_movimiento == 2:  # Egreso / Venta
            self.saldo_cantidad = saldo_cantidad_anterior - self.cantidad
            self.saldo_costo = saldo_costo_anterior - self.costo_total
            self.saldo_ganancia = ganancia_total

        # Guardar el registro actualizado
        super(KardexProducto, self).save(*args, **kwargs)



class Venta(ModeloBase):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Nombre del Cliente')
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, blank=True, null=True, related_name='ventatrabajador', verbose_name=u'Trabajador')
    fecha_venta = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Venta')
    descuento = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Descuento')
    preciov = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio de la venta')
    detalle = models.CharField(max_length=2000, blank=True, null=True, verbose_name=u'Detalle')

    def productos_vendidos(self):
        detalles = self.detalleventa.all()
        return "<br>".join([f"{detalle.producto.nombre.upper()} x <b>{detalle.cantidad}</b> x ${detalle.preciou}" for detalle in detalles])

    def subtotal(self):
        detalles = self.detalleventa.all()
        return sum(detalle.preciot for detalle in detalles)

class VentaDetalle(ModeloBase):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalleventa', verbose_name=u'Venta')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, blank=True, null=True, related_name='venta', verbose_name=u'Producto')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    preciou = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del producto')
    preciot = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio Total')

class Trabajo(ModeloBase):
    nombre = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Nombre de Trabajo')
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del Trabajo')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')

    def __str__(self):
        return f'{self.nombre}'

class TrabajoDia(ModeloBase):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Nombre del Trabajador', related_name='trabajos_dia')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Nombre del Cliente', related_name='mantenimientos')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')
    descuento = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Descuento')
    preciot = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio Total')
    fecha_servicio = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha del Servicio')

    def __str__(self):
        return f'${self.preciot}'

    def trabajos_realizados(self):
        detalles = self.trabajodiadetalle.all()
        return "<br>".join([f"{detalle.trabajo} x <b>{detalle.cantidad}</b> x ${detalle.preciou}" for detalle in detalles])

    def subtotal(self):
        detalles = self.trabajodiadetalle.all()
        return sum(detalle.preciot for detalle in detalles)

class TrabajoDiaDetalle(ModeloBase):
    trabajodia = models.ForeignKey(TrabajoDia, on_delete=models.CASCADE, verbose_name=u'TrabajoDia', related_name='trabajodiadetalle')
    trabajo = models.ForeignKey(Trabajo, on_delete=models.CASCADE, verbose_name='Trabajo', related_name='trabajodetalle')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'')
    preciou = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio del producto')
    preciot = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio Total')

class GastoNoOperativo(ModeloBase):
    titulo = models.CharField(blank=True, null=True, max_length=500, verbose_name=u'Titulo del Gasto')
    detalle = models.CharField(blank=True, null=True, verbose_name=u'Titulo del Gasto', max_length=2000)
    valor = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Valor del Gasto')

ESTADO_VENTA = (
    (0, u'TODO'),
    (1, u'PENDIENTE'),
    (2, u'PAGADO')
)

class vVenta(ModeloBase):
    fecha_venta = models.DateTimeField(blank=True, null=True, verbose_name=u'Fecha de Venta')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Nombre del Cliente', related_name='trabajos')
    descuento = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Descuento')
    totalventa = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio Total')
    subtotalventa = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Subtotal')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')
    abono = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Abono')
    estado = models.IntegerField(default=1, choices=ESTADO_VENTA, blank=True, null=True, verbose_name=u'Estado de la Venta')

    def obtener_detalles(self):
        detalles = []

        # Obtener detalles de productos
        for detalle in self.detalleproducto.all():
            detalles.append(f"<li><b>{detalle.producto.nombre}</b> x <b>{detalle.cantidad}</b> x <b>${detalle.preciounitario}</b></li>")

        # Obtener detalles de servicios
        for detalle in self.detalleservicio.all():
            detalles.append(f"<li><b>{detalle.servicio}</b> x <b>{detalle.cantidad}</b> x <b>${detalle.total}</b></li>")

        # Obtener detalles adicionales
        for detalle in self.detalleadicional.all():
            detalles.append(f"<li><b>{detalle.detalle}</b> x <b>${detalle.precio}</b></li>")

        return "\n".join(detalles)

    def obtener_detalles_excel(self):
        detalles = []

        # Obtener detalles de productos
        for detalle in self.detalleproducto.all():
            detalles.append(f"{detalle.producto.nombre} x {detalle.cantidad} x ${detalle.preciounitario}")

        # Obtener detalles de servicios
        for detalle in self.detalleservicio.all():
            detalles.append(f"{detalle.servicio} x {detalle.cantidad} x ${detalle.total}")

        # Obtener detalles adicionales
        for detalle in self.detalleadicional.all():
            detalles.append(f"{detalle.detalle} x ${detalle.precio}")

        return "\n".join(detalles)

    def obtener_deuda(self):
        return f'<b style="color: salmon">${self.totalventa - self.abono}</b>'

class VentaProductoDetalle(ModeloBase):
    venta = models.ForeignKey(vVenta, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Venta', related_name='detalleproducto')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name=u'Producto', related_name='productoventa')
    lote = models.ForeignKey(LoteProducto, on_delete=models.CASCADE, verbose_name=u'Lote', related_name='detalleventa')
    preciounitario = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio Unitario')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Total')

class VentaServicioDetalle(ModeloBase):
    venta = models.ForeignKey(vVenta, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Venta', related_name='detalleservicio')
    servicio = models.ForeignKey(Trabajo, on_delete=models.CASCADE, verbose_name=u'servicio', related_name='servicioventa')
    cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    total = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Total')

class VentaAdicionalDetalle(ModeloBase):
    venta = models.ForeignKey(vVenta, on_delete=models.CASCADE, blank=True, null=True, verbose_name=u'Venta', related_name='detalleadicional')
    detalle = models.CharField(max_length=5000, blank=True, null=True, verbose_name=u'Detalle del Trabajo')
    # cantidad = models.IntegerField(blank=True, null=True, verbose_name=u'Cantidad')
    precio = models.DecimalField(default=0, max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=u'Precio')

