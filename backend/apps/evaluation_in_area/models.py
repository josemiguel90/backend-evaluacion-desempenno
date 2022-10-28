from datetime import date

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..charge.models import Charge
from ..payTime.models import PayTime
from ..workers.models import Worker


class EvaluationArea(models.Model):

    name = models.CharField(max_length=80, null=False, unique=True)
    boss_charge = models.ForeignKey(Charge, on_delete=models.PROTECT, null=False)


class EvaluationAspect(models.Model):

    SELECTABLE_TYPE = 'SELECTABLE'
    SALE_PLAN_FULFILMENT_TYPE = 'SALE_PLAN_FULFILMENT'
    CHECK_LIST_TYPE = 'CHECK_LIST'

    name = models.CharField(max_length=80, null=False)
    bad_option = models.CharField(max_length=80, null=False)
    regular_option = models.CharField(max_length=80, null=False)
    good_option = models.CharField(max_length=80, null=False)
    very_good_option = models.CharField(max_length=80, null=False)
    type = models.CharField(null=False,
                            max_length=30,
                            default=SELECTABLE_TYPE,
                            choices=((SELECTABLE_TYPE, SELECTABLE_TYPE),
                                     (SALE_PLAN_FULFILMENT_TYPE, SALE_PLAN_FULFILMENT_TYPE),
                                     (CHECK_LIST_TYPE, CHECK_LIST_TYPE)))
    related_melia_aspect = models.ForeignKey(to='MeliaAspect', on_delete=models.PROTECT,
                                             related_name='evaluations_aspects')
    area = models.ForeignKey(to=EvaluationArea, on_delete=models.PROTECT, related_name='aspects')
    active = models.BooleanField(null=False)


class MeliaAspect(models.Model):

    name = models.CharField(max_length=80, null=False)


class MonthEvaluation(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['evaluation_area', 'worker', 'payment_period'],
                                    name='unique_month_evaluation')
        ]

    evaluation_area = models.ForeignKey(to=EvaluationArea, on_delete=models.PROTECT)
    date = models.DateField(default=date.today)
    worker = models.ForeignKey(to=Worker, on_delete=models.PROTECT, related_name='+')
    worker_charge = models.ForeignKey(to=Charge, on_delete=models.PROTECT, related_name='+')
    evaluator = models.CharField(max_length=100, null=False)
    evaluator_charge = models.ForeignKey(to=Charge, on_delete=models.PROTECT, related_name='+')
    payment_period = models.ForeignKey(to=PayTime, on_delete=models.PROTECT)
    evaluated_aspect = models.ManyToManyField(EvaluationAspect, through='MonthEvaluationAspectValue',
                                              through_fields=['month_evaluation', 'aspect'])
    evaluated_melia_aspect = models.ManyToManyField(MeliaAspect, through='MeliaMonthEvaluationAspectValue',
                                                    through_fields=['month_evaluation', 'melia_aspect'])


class MonthEvaluationAspectValue(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['month_evaluation', 'aspect'],
                                    name='unique_evaluated_aspect')
        ]

    month_evaluation = models.ForeignKey(to=MonthEvaluation, on_delete=models.CASCADE)
    aspect = models.ForeignKey(to=EvaluationAspect, on_delete=models.CASCADE)
    assigned_value = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])


class MeliaMonthEvaluationObservation(models.Model):

    id = models.OneToOneField(MonthEvaluation, on_delete=models.CASCADE, related_name='melia_observation',
                              primary_key=True)
    observations = models.CharField(max_length=300, null=True)


class MeliaMonthEvaluationAspectValue(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['month_evaluation', 'melia_aspect'],
                                    name='unique_melia_evaluation_aspect_value')
        ]

    month_evaluation = models.ForeignKey(to=MonthEvaluation, on_delete=models.CASCADE,
                                         related_name='melia_aspects')
    melia_aspect = models.ForeignKey(to=MeliaAspect, on_delete=models.CASCADE)
    assigned_value = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])
