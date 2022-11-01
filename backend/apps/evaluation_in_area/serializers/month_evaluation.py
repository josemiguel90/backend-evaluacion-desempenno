import statistics

from rest_framework import serializers

from .evaluation_area import EvaluationAreaSerializer
from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue
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

    class Meta:
        model = MonthEvaluation
        fields = ['id', 'date', 'evaluation_area', 'worker', 'worker_charge', 'evaluator', 'evaluator_charge',
                  'payment_period', 'aspects_with_value']

    def get_aspects_with_value(self, obj):
        valued_aspects = MonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        valued_aspects_serializer = MonthEvaluationAspectValueSerializer(valued_aspects, many=True)
        return valued_aspects_serializer.data


class SimpleMonthEvaluationSerializer(MonthEvaluationSerializer):
    """
    Este serializer no tiene todos los valores númericos asignados a los aspectos, en vez de eso
    posee un atributo con la nota promedio o final de la evaluación.
    """
    final_note = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MonthEvaluation
        fields = ['id', 'date', 'evaluation_area', 'worker', 'worker_charge', 'evaluator', 'evaluator_charge',
                  'payment_period', 'final_note']

    def get_final_note(self, obj):
        valued_aspects = MonthEvaluationAspectValue.objects.filter(month_evaluation=obj)
        values_in_evaluation = valued_aspects.values_list('assigned_value', flat=True)

        if len(values_in_evaluation) == 0:
            return None

        mean_evaluation_value = statistics.mean(values_in_evaluation)

        if 2 <= mean_evaluation_value < 3:
            return 'M'
        elif 3 <= mean_evaluation_value < 4:
            return 'R'
        elif 4 <= mean_evaluation_value < 5:
            return 'B'
        elif mean_evaluation_value == 5:
            return 'MB'
        raise Exception(f'Mean value must be between 2 and 5. Found {mean_evaluation_value}')
