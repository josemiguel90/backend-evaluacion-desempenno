from rest_framework import serializers
from apps.evaluation_in_area.models import EvaluationArea


class EvaluationAreaSerializer(serializers.ModelSerializer):

    charge_description = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = EvaluationArea
        fields = ['id', 'name', 'boss_charge', 'charge_description']

    def get_charge_description(self, obj):
        return obj.boss_charge.descripcion.title()