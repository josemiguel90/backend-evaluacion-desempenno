from django.db import models
from ..charge.models import Charge
from ..category.models import OccupationalCategory
from ..hotel.models import Hotel


class Operador(models.Model):
    id_oper = models.IntegerField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=30)
    descripcion = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f'Operador {self.descripcion} {self.worker}'


class Worker(models.Model):
    no_interno = models.CharField(primary_key=True, max_length=7, default='')
    nombre = models.CharField(max_length=50, default='')
    apell1 = models.CharField(max_length=50, default='')
    apell2 = models.CharField(max_length=50, default='')
    unidad_org = models.ForeignKey(Hotel, models.PROTECT, related_name='workers', default=None)
    cat_ocup = models.ForeignKey(OccupationalCategory, models.PROTECT, default=None, null=True)
    cargo = models.ForeignKey(Charge, models.PROTECT, default=None, null=True)
    activo = models.BooleanField(default=False)
    operador = models.OneToOneField(Operador, on_delete=models.PROTECT, default=None, null=True, related_name='worker')
    area_evaluacion = models.ForeignKey('evaluation_in_area.EvaluationArea', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Trabajador: {self.nombre} - {self.apell1}'

    def nombreCompleto(self):
        return f'{self.nombre} {self.apell1} {self.apell2}'.title()
