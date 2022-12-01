from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.viewsets import ModelViewSet

from apps.charge.models import Charge
from apps.charge.serializers import ChargeSerializer
from apps.evaluation_in_area.models import EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_area import EvaluationAreaSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action

from apps.evaluation_in_area.util import handle_evaluation_area_validation_error, check_area_name_is_not_used
from apps.users.models import User
from apps.workers.models import Worker


class EvaluationAreaViewSet(ModelViewSet):

    queryset = EvaluationArea.objects.filter(active=True).all()
    serializer_class = EvaluationAreaSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            name = request.data['name']
            bad_request_response = check_area_name_is_not_used(name)
            if bad_request_response:
                return bad_request_response
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return handle_evaluation_area_validation_error(e, request)

    def update(self, request, *args, **kwargs):
        try:
            name = request.data['name']
            area = self.get_object()
            bad_request_response = check_area_name_is_not_used(name, area.id)
            if bad_request_response:
                return bad_request_response
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return handle_evaluation_area_validation_error(e, request)

    @action(methods=['POST'], url_path='delete', detail=False)
    def delete_areas(self, request):
        try:
            for evaluation_area in request.data:
                area = EvaluationArea.objects.filter(active=True)\
                    .get(pk=evaluation_area.get('id'))
                area.active = False
                area.save()

                # Desvincluar a los trabajadores del área
                workers_from_area = Worker.objects.filter(area_evaluacion=area)
                for a_worker in workers_from_area:
                    a_worker.area_evaluacion = None
                    a_worker.save()

                # Eliminar usuario evaluador vinculado con el área
                users = User.objects.get(area=area).delete()

            return Response({'Evaluation Areas eliminated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], url_path='available', detail=False)
    def get_unassigned_evaluation_areas(self, request):
        users_with_area = User.objects.exclude(area=None).select_related('area')
        assigned_areas_id = list(map(lambda a_user: a_user.area.id, users_with_area))

        available_areas = EvaluationArea.objects.filter(active=True).exclude(id__in=assigned_areas_id).all()
        area_serializer = EvaluationAreaSerializer(available_areas, many=True)
        return Response(area_serializer.data, status.HTTP_200_OK)

    @action(methods=['GET'], url_path='available-charges', detail=False, permission_classes=[IsAdminUser])
    def get_available_charges_for_areas(self, request):
        used_charge_ids: List[int] = EvaluationArea.objects.filter(active=True)\
            .values_list('boss_charge', flat=True)
        available_charges = Charge.objects.exclude(id_cargos__in=used_charge_ids).order_by('descripcion')
        serializer = ChargeSerializer(available_charges, many=True)
        return Response(serializer.data, status.HTTP_200_OK)
