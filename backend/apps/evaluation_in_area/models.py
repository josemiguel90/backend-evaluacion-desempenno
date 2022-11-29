from datetime import date
from typing import List

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ..charge.models import Charge
from ..payTime.models import PayTime
from ..workers.models import Worker


class EvaluationArea(models.Model):

    GASTRONOMY_TYPE = 'gastronomy'
    HOUSEKEEPER_TYPE = 'housekeeper'

    name = models.CharField(max_length=80, null=False)
    boss_charge = models.ForeignKey(Charge, on_delete=models.PROTECT, null=False)
    type = models.CharField(choices=((GASTRONOMY_TYPE, GASTRONOMY_TYPE),
                                     (HOUSEKEEPER_TYPE, HOUSEKEEPER_TYPE)),
                            unique=True,
                            null=True,
                            default=None,
                            max_length=30)
    active = models.BooleanField(default=True)


class EvaluationAspect(models.Model):

    SELECTABLE_TYPE = 'SELECTABLE'
    SALE_PLAN_FULFILMENT_TYPE = 'SALE_PLAN_FULFILMENT'
    CHECK_LIST_TYPE = 'CHECK_LIST'

    name = models.CharField(max_length=180, null=False)
    bad_option = models.CharField(max_length=180, null=False)
    regular_option = models.CharField(max_length=180, null=False)
    good_option = models.CharField(max_length=180, null=False)
    very_good_option = models.CharField(max_length=180, null=False)
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
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(null=False)


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
    evaluator = models.ForeignKey(to=Worker, on_delete=models.PROTECT)
    evaluator_charge = models.ForeignKey(to=Charge, on_delete=models.PROTECT, related_name='+')
    payment_period = models.ForeignKey(to=PayTime, on_delete=models.PROTECT)
    evaluated_aspect = models.ManyToManyField(EvaluationAspect, through='MonthEvaluationAspectValue',
                                              through_fields=['month_evaluation', 'aspect'])
    evaluated_melia_aspect = models.ManyToManyField(MeliaAspect, through='MeliaMonthEvaluationAspectValue',
                                                    through_fields=['month_evaluation', 'melia_aspect'])
    melia_observations = models.CharField(max_length=500, default='')

    def get_melia_final_note(self):
        melia_aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=self)
        values_in_evaluation: List[int] = list(melia_aspects_with_value.values_list('assigned_value', flat=True))

        if len(values_in_evaluation) == 0:
            raise Exception(f'No melia values for evaluation with id {self.id}')

        total = sum(values_in_evaluation, 0)
        final_note = 'M'

        if 14 <= total <= 20:
            final_note = 'M'
        elif 21 <= total <= 27:
            final_note = 'R'
        elif 28 <= total <= 31:
            final_note = 'B'
        elif 32 <= total <= 35:
            final_note = 'MB'
        else:
            raise Exception(f'Total of melia evaluation values are not between 14 and 35: {total}')

        # Condiciones especiales para las evaluaciones

        # La nota no puede ser MB si se obtuvo una de Mal o Regular
        if final_note == 'MB' and (values_in_evaluation.count(2) > 0 or values_in_evaluation.count(3) > 0):
            final_note = 'B'

        # La nota no puede ser B si se obtuvo alguna nota de Mal
        if final_note == 'B' and values_in_evaluation.count(2) > 0:
            final_note = 'R'

        return final_note

    def melia_total_points(self):
        total = 0
        aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=self.id)
        for aspect_with_value in aspects_with_value:
            total += aspect_with_value.assigned_value
        return total

class MonthEvaluationAspectValue(models.Model):

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['month_evaluation', 'aspect'],
                                    name='unique_evaluated_aspect')
        ]

    month_evaluation = models.ForeignKey(to=MonthEvaluation, on_delete=models.CASCADE)
    aspect = models.ForeignKey(to=EvaluationAspect, on_delete=models.CASCADE)
    assigned_value = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])


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


class YearMeliaEvaluation(models.Model):

    DEFICIENT_EVALUATION = 'Deficiente'
    APPROPRIATE_EVALUATION = 'Adecuado'
    SUPERIOR_EVALUATION = 'Superior'

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'worker', 'evaluation_area'],
                                    name='unique_year_evaluation')
        ]

    year = models.IntegerField(validators=[MinValueValidator(1950)])
    worker = models.ForeignKey(to=Worker, null=False, on_delete=models.RESTRICT, related_name='+')
    worker_charge = models.ForeignKey(to=Charge, null=False, on_delete=models.RESTRICT, related_name='+')
    evaluator = models.ForeignKey(to=Worker, null=False, on_delete=models.RESTRICT, related_name='+')
    evaluator_charge = models.ForeignKey(to=Charge, null=False, on_delete=models.RESTRICT, related_name='+')
    evaluation_area = models.ForeignKey(to=EvaluationArea, on_delete=models.RESTRICT, related_name='+')
    date = models.DateField(default=date.today, null=False)

    # Indicadores
    summary = models.CharField(max_length=500)
    fulfillment = models.CharField(max_length=500)
    behavior = models.CharField(max_length=500)
    use_and_care = models.CharField(max_length=500)
    recommendation = models.CharField(max_length=500)

    final_evaluation = models.CharField(max_length=20,
                                        choices=[(DEFICIENT_EVALUATION, DEFICIENT_EVALUATION),
                                                 (APPROPRIATE_EVALUATION, APPROPRIATE_EVALUATION),
                                                 (SUPERIOR_EVALUATION, SUPERIOR_EVALUATION)])
