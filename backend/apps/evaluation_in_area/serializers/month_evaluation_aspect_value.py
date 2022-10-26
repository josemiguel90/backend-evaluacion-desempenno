from rest_framework import serializers

from apps.evaluation_in_area.models import MonthEvaluationAspectValue
from apps.evaluation_in_area.serializers.evaluation_aspect import EvaluationAspectSerializer


class MonthEvaluationAspectValueSerializer(serializers.ModelSerializer):

    aspect = EvaluationAspectSerializer(read_only=True)

    class Meta:
        model = MonthEvaluationAspectValue
        fields = ['month_evaluation', 'aspect', 'assigned_value']