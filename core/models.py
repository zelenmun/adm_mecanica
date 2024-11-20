from django.db import models
from datetime import datetime, timedelta, date, time
from mecanica.settings import ADMINISTRADOR_ID

class ModeloBase(models.Model):
    from django.contrib.auth.models import User
    status = models.BooleanField(default=True)
    usuario_creacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    usuario_modificacion = models.ForeignKey(User, on_delete=models.PROTECT, related_name='+', blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        usuario = None
        if len(args):
            usuario = args[0].user.id
        if self.id:
            self.usuario_modificacion_id = usuario if usuario else ADMINISTRADOR_ID
            self.fecha_modificacion = datetime.now()
        else:
            self.usuario_creacion_id = usuario if usuario else ADMINISTRADOR_ID
            self.fecha_creacion = datetime.now()
        models.Model.save(self)

    class Meta:
        abstract = True

class Persona(ModeloBase):
    cedula = models.CharField(max_length=10, blank=True, null=True, verbose_name=u'Cédula')
    nombre = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'Nombre')
    apellido1 = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'Primer apellido')
    apellido2 = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'Segundo apellido')
    direccion = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Dirección')
    celular = models.CharField(max_length=500, blank=True, null=True, verbose_name=u'Numero de Celular')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name=u'Fecha de nacimiento')
    correo = models.CharField(max_length=200, blank=True, null=True, verbose_name=u'Email')