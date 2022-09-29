from rest_framework import serializers
from apps.evaluation_in_area.models import EvaluationArea


class EvaluationAreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvaluationArea
        fields = '__all__'
