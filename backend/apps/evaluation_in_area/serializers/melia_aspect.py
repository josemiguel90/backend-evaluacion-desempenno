from rest_framework.serializers import ModelSerializer
from apps.evaluation_in_area.models import MeliaAspect


class MeliaAspectSerializer(ModelSerializer):

    class Meta:
        model = MeliaAspect
        fields = '__all__'
