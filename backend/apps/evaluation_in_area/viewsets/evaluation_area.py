from rest_framework.viewsets import ModelViewSet
from apps.evaluation_in_area.models import EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_area import EvaluationAreaSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class EvaluationAreaViewSet(ModelViewSet):

    queryset = EvaluationArea.objects.all()
    serializer_class = EvaluationAreaSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
