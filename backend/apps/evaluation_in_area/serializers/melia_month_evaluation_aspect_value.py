from rest_framework.serializers import ModelSerializer
from apps.evaluation_in_area.models import MeliaMonthEvaluationAspectValue
from apps.evaluation_in_area.serializers.melia_aspect import MeliaAspectSerializer


class MeliaMonthEvaluationAspectValueSerializer(ModelSerializer):

    melia_aspect = MeliaAspectSerializer(read_only=True)

    class Meta:
        model = MeliaMonthEvaluationAspectValue
        fields = ['id', 'month_evaluation', 'melia_aspect', 'assigned_value']
