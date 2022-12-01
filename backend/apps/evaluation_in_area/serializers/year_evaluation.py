from datetime import timedelta, date

from rest_framework import serializers
from apps.evaluation_in_area.models import YearMeliaEvaluation
from apps.workers.serializers import WorkerSerializer


class YearMeliaEvaluationSerializer(serializers.ModelSerializer):

    worker = WorkerSerializer(read_only=True)
    evaluator = WorkerSerializer(read_only=True)
    evaluation_area = serializers.SerializerMethodField(read_only=True)
    can_be_modified = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = YearMeliaEvaluation
        fields = ['id', 'year', 'date', 'worker', 'evaluator', 'evaluation_area', 'summary',
                  'fulfillment', 'behavior', 'use_and_care', 'recommendation', 'final_evaluation',
                  'can_be_modified']

    def get_evaluation_area(self, obj):
        return obj.evaluation_area.name

    def get_can_be_modified(self, evaluation: YearMeliaEvaluation):
        thirty_days = timedelta(days=30)
        today = date.today()
        return today - evaluation.date < thirty_days


class SimpleYearMeliaEvaluationSerializer(serializers.ModelSerializer):

    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = YearMeliaEvaluation
        fields = ['id', 'year', 'worker', 'final_evaluation']
