from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.evaluation_in_area.models import EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_area import EvaluationAreaSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

class EvaluationAreaViewSet(ModelViewSet):

    queryset = EvaluationArea.objects.all()
    serializer_class = EvaluationAreaSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_areas(self, request):
        try:
            for evaluation_area in request.data:
                self.queryset.get(pk=evaluation_area.get('id')).delete()
            return Response({'Evaluation Areas eliminated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
