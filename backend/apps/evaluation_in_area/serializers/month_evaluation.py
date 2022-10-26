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
