from django.db import models
from datetime import datetime, timedelta, date, time
from mecanica.settings import ADMINISTRADOR_ID

class ModeloBase(models.Model):
    status = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.id:
            self.fecha_modificacion = datetime.now()
        else:
            self.fecha_creacion = datetime.now()
        super().save(*args, **kwargs)

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

    def __str__(self):
        return f'{self.nombre} {self.apellido1} {self.apellido2}'