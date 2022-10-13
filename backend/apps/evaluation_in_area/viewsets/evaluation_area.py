from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.evaluation_in_area.models import EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_area import EvaluationAreaSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from apps.users.models import User


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

    @action(methods=['GET'], url_path='available', detail=False)
    def get_unassigned_evaluation_areas(self, request):
        users_with_area = User.objects.exclude(area=None).select_related('area')
        assigned_areas_id = list(map(lambda a_user: a_user.area.id, users_with_area))

        available_areas = EvaluationArea.objects.exclude(id__in=assigned_areas_id).all()
        area_serializer = EvaluationAreaSerializer(available_areas, many=True)
        return Response(area_serializer.data, status.HTTP_200_OK)

