from rest_framework.serializers import ModelSerializer
from apps.evaluation_in_area.models import EvaluationAspect


class EvaluationAspectSerializer(ModelSerializer):

    class Meta:
        model = EvaluationAspect
        fields = '__all__'
