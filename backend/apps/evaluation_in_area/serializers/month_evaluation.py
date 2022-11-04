import statistics

from rest_framework import serializers

from .evaluation_area import EvaluationAreaSerializer
from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue, MeliaMonthEvaluationAspectValue
from .melia_month_evaluation_aspect_value import MeliaMonthEvaluationAspectValueSerializer
from .month_evaluation_aspect_value import MonthEvaluationAspectValueSerializer
from ...charge.serializers import ChargeSerializer
from ...payTime.serializers import PayTimeSerializer
from ...workers.serializers import WorkerSerializer


class MonthEvaluationSerializer(serializers.ModelSerializer):

    evaluation_area = EvaluationAreaSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)
    worker_charge = ChargeSerializer(read_only=True)
    evaluator_charge = ChargeSerializer(read_only=True)
    payment_period = PayTimeSerializer(read_only=True)
    aspects_with_value = serializers.SerializerMethodField(read_only=True)
    melia_aspects_with_value = serializers.SerializerMethodField(read_only=True)
    final_note = serializers.SerializerMethodField(read_only=True)
    final_melia_note = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MonthEvaluation
        fields = ['id', 'date', 'evaluation_area', 'worker', 'worker_charge', 'evaluator', 'evaluator_charge',
                  'payment_period', 'aspects_with_value', 'melia_aspects_with_value', 'final_note',
                  'final_melia_note']

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
        melia_aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        values_in_evaluation = melia_aspects_with_value.values_list('assigned_value', flat=True)

        if len(values_in_evaluation) == 0:
            raise Exception(f'No melia values for evaluation with id {obj.id}')

        value = round(statistics.mean(values_in_evaluation))

        if value == 2:
            return 'M'
        elif value == 3:
            return 'R'
        elif value == 4:
            return 'B'
        elif value == 5:
            return 'MB'
        raise Exception(f'Melia evaluation mean value must be between 2, 3, 4 or 5. Found {value}')


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
                  'payment_period', 'final_note', 'final_melia_note']

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
        melia_aspects_with_value = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        values_in_evaluation = melia_aspects_with_value.values_list('assigned_value', flat=True)

        if len(values_in_evaluation) == 0:
            raise Exception(f'No melia values for evaluation with id {obj.id}')

        value = round(statistics.mean(values_in_evaluation))

        if value == 2:
            return 'M'
        elif value == 3:
            return 'R'
        elif value == 4:
            return 'B'
        elif value == 5:
            return 'MB'
        raise Exception(f'Melia evaluation mean value must be between 2, 3, 4 or 5. Found {value}')
