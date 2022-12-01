import statistics
from datetime import timedelta, date
from typing import List

from django.utils import timezone
from rest_framework import serializers

from .evaluation_area import EvaluationAreaSerializer
from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue, MeliaMonthEvaluationAspectValue
from .melia_month_evaluation_aspect_value import MeliaMonthEvaluationAspectValueSerializer
from .month_evaluation_aspect_value import MonthEvaluationAspectValueSerializer
from ...charge.serializers import ChargeSerializer
from ...payTime.serializers import PayTimeSerializer
from ...workers.serializers import WorkerSerializer


def calculate_final_melia_note(obj):
    melia_aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
    values_in_evaluation: List[int] = list(melia_aspects_with_value.values_list('assigned_value', flat=True))

    if len(values_in_evaluation) == 0:
        raise Exception(f'No melia values for evaluation with id {obj.id}')

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


class MonthEvaluationSerializer(serializers.ModelSerializer):

    evaluation_area = EvaluationAreaSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    worker_charge = ChargeSerializer(read_only=True)
    evaluator = WorkerSerializer(read_only=True)
    evaluator_charge = ChargeSerializer(read_only=True)
    payment_period = PayTimeSerializer(read_only=True)
    aspects_with_value = serializers.SerializerMethodField(read_only=True)
    melia_aspects_with_value = serializers.SerializerMethodField(read_only=True)
    final_note = serializers.SerializerMethodField(read_only=True)
    final_melia_note = serializers.SerializerMethodField(read_only=True)
    can_be_modified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MonthEvaluation
        fields = ['id', 'date', 'evaluation_area', 'worker', 'worker_charge', 'evaluator', 'evaluator_charge',
                  'payment_period', 'aspects_with_value', 'melia_aspects_with_value', 'final_note',
                  'final_melia_note', 'melia_observations', 'can_be_modified']

    def get_aspects_with_value(self, obj):
        valued_aspects = MonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        valued_aspects_serializer = MonthEvaluationAspectValueSerializer(valued_aspects, many=True)
        return valued_aspects_serializer.data

    def get_melia_aspects_with_value(self, obj):
        melia_aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        serializer = MeliaMonthEvaluationAspectValueSerializer(melia_aspects_with_value, many=True)
        return serializer.data

    def get_final_note(self, obj):
        valued_aspects = MonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        values_in_evaluation = valued_aspects.values_list('assigned_value', flat=True)

        if len(values_in_evaluation) == 0:
            return None

        value = round(statistics.mean(values_in_evaluation))

        if value == 2:
            return 'M'
        elif value == 3:
            return 'R'
        elif value == 4:
            return 'B'
        elif value == 5:
            return 'MB'

    def get_final_melia_note(self, obj):
        return calculate_final_melia_note(obj)

    def get_can_be_modified(self, evaluation: MonthEvaluation):
        thirty_days = timedelta(days=30)
        today = date.today()
        return today - evaluation.date < thirty_days


class SimpleMonthEvaluationSerializer(MonthEvaluationSerializer):
    """
    Este serializer no tiene todos los valores númericos asignados a los aspectos, en vez de eso
    posee atributos con la nota final de la evaluación mensual del área y de Meliá.
    """
    final_note = serializers.SerializerMethodField(read_only=True)
    final_melia_note = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MonthEvaluation
        fields = ['id', 'date', 'evaluation_area', 'worker', 'worker_charge', 'evaluator', 'evaluator_charge',
                  'payment_period', 'final_note', 'final_melia_note', 'can_be_modified']

    def get_final_note(self, obj):
        valued_aspects = MonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        values_in_evaluation = valued_aspects.values_list('assigned_value', flat=True)

        if len(values_in_evaluation) == 0:
            return None

        value = round(statistics.mean(values_in_evaluation))

        if value == 2:
            return 'M'
        elif value == 3:
            return 'R'
        elif value == 4:
            return 'B'
        elif value == 5:
            return 'MB'

    def get_final_melia_note(self, obj):
        return calculate_final_melia_note(obj)