from typing import List, OrderedDict

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.evaluation_in_area.models import EvaluationAspect, MeliaAspect, EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_aspect import EvaluationAspectSerializer
from apps.evaluation_in_area.util import find_aspect_with_id_in_list
from backend.extraPermissions import IsEvaluatorFromArea


class EvaluationAspectViewSet(ModelViewSet):

    queryset = EvaluationAspect.objects
    serializer_class = EvaluationAspectSerializer
    permission_classes = [IsEvaluatorFromArea]

    def list(self, request, *args, **kwargs):
        aspects = EvaluationAspect.objects.filter(area=request.user.area)
        aspect_serializer = EvaluationAspectSerializer(aspects, many=True)
        return Response(aspect_serializer.data, status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='active', permission_classes=[IsEvaluatorFromArea])
    def available_aspects(self, request):
        aspects = EvaluationAspect.objects.filter(area=request.user.area).filter(active=True)
        aspect_serializer = EvaluationAspectSerializer(aspects, many=True)
        return Response(aspect_serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            related_melia_aspect = MeliaAspect.objects.get(pk=data.get('related_melia_aspect'))

            aspect = EvaluationAspect(
                name=data.get('name'),
                bad_option=data.get('bad_option'),
                regular_option=data.get('regular_option'),
                good_option=data.get('good_option'),
                very_good_option=data.get('very_good_option'),
                type=data.get('type'),
                related_melia_aspect=related_melia_aspect,
                area=request.user.area,
                active=True)
            aspect.save()

            aspect_serializer = EvaluationAspectSerializer(aspect)
            return Response(aspect_serializer.data, status.HTTP_201_CREATED)

        except MeliaAspect.DoesNotExist:
            return Response({'detail': f'El parametro de Melia con id {data.get("related_melia_aspect")} no existe'},
                            status.HTTP_404_NOT_FOUND)
        except EvaluationArea.DoesNotExist:
            return Response({'detail': f'El Area de evaluacion con id {data.get("area")} no existe'},
                            status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': e.args[0]}, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        aspect: EvaluationAspect = self.get_object()
        aspect.active = False
        aspect.save()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        aspect: EvaluationAspect = self.get_object()
        data = request.data

        if not aspect.active:
            return Response({'detail': 'Este indicador ya fue marcado como eliminado'}, status.HTTP_400_BAD_REQUEST)
        if data.get('area') and data.get('area') != aspect.area.id:
            return Response({'detail': 'El area de los indicadores no puede ser cambiada'},
                            status.HTTP_400_BAD_REQUEST)
        try:
            melia_aspect = MeliaAspect.objects.get(pk=data.get('related_melia_aspect'))

            aspect.name = data.get('name')
            aspect.bad_option = data.get('bad_option')
            aspect.regular_option = data.get('regular_option')
            aspect.good_option = data.get('good_option')
            aspect.very_good_option = data.get('very_good_option')
            aspect.related_melia_aspect = melia_aspect
            aspect.save()

            aspect_serializer = EvaluationAspectSerializer(aspect)
            return Response(aspect_serializer.data, status.HTTP_200_OK)

        except MeliaAspect.DoesNotExist:
            return Response({'detail': f'No existe el indicador de Melia con el id {data.get("related_melia_aspect")}'},
                            status.HTTP_404_NOT_FOUND)

    @action(detail=False, url_path='change', methods=['POST'], permission_classes=[IsEvaluatorFromArea])
    def change_current_indicator_for_user(self, request):

        aspects_to_update = self.get_objects_to_update(request)
        new_aspects = self.create_new_aspects_instances(request)
        aspects_to_delete = self.get_aspects_to_delete(request, aspects_to_update)

        try:
            self.update_aspects(aspects_to_update, request)
            # se deben eliminar los aspectos primero, ya que si se crean algunos primero,
            # los nuevos aspectos serán eliminados porque no están en la lista de los
            # aspectos actualizados
            self.delete_aspects(aspects_to_delete)
            self.create_aspects(new_aspects, request)
        except Exception as e:
            raise e
            # return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

        active_aspects = EvaluationAspect.objects.filter(area=request.user.area).filter(active=True)
        aspect_serializer = EvaluationAspectSerializer(data=active_aspects, many=True)
        aspect_serializer.is_valid()
        return Response(aspect_serializer.data, status.HTTP_200_OK)

    @staticmethod
    def get_objects_to_update(request) -> List[EvaluationAspect]:
        user = request.user
        aspects_with_id = list(filter(lambda an_aspect: an_aspect['id'] is not None, request.data))
        ids = list(map(lambda an_aspect: an_aspect['id'], aspects_with_id))
        user_aspect_queryset = EvaluationAspect.objects.filter(area=user.area)
        return user_aspect_queryset.filter(id__in=ids).all()

    @staticmethod
    def create_new_aspects_instances(request) -> List[OrderedDict]:
        aspects_without_ids = list(filter(lambda an_aspect: an_aspect['id'] is None, request.data))
        aspect_serializer = EvaluationAspectSerializer(data=aspects_without_ids, many=True)
        aspect_serializer.is_valid()
        return aspect_serializer.validated_data

    @staticmethod
    def get_aspects_to_delete(request, aspects_to_update: List[EvaluationAspect]) -> List[EvaluationAspect]:
        """Obtener los aspectos que no van a ser actualizados, y que deben ser marcados como desactivados"""
        aspects_to_update_ids = list(map(lambda an_aspect: an_aspect.id, aspects_to_update))
        active_aspects_of_user = EvaluationAspect.objects.filter(area=request.user.area).filter(active=True)

        return active_aspects_of_user.exclude(id__in=aspects_to_update_ids).all()

    @staticmethod
    def update_aspects(aspects_to_update: List[EvaluationAspect], request):
        for an_aspect in aspects_to_update:

            updated_aspect = find_aspect_with_id_in_list(an_aspect.id, request.data)
            melia_aspect = get_object_or_404(MeliaAspect, pk=updated_aspect['related_melia_aspect'])

            an_aspect.name = updated_aspect['name']
            an_aspect.bad_option = updated_aspect['bad_option']
            an_aspect.regular_option = updated_aspect['regular_option']
            an_aspect.good_option = updated_aspect['good_option']
            an_aspect.very_good_option = updated_aspect['very_good_option']
            an_aspect.related_melia_aspect = melia_aspect

            an_aspect.save()

    @staticmethod
    def create_aspects(new_aspect_dicts: List[OrderedDict], request):
        for a_new_aspect_dict in new_aspect_dicts:
            area = request.user.area
            EvaluationAspect(name=a_new_aspect_dict['name'],
                             bad_option=a_new_aspect_dict['bad_option'],
                             regular_option=a_new_aspect_dict['regular_option'],
                             good_option=a_new_aspect_dict['good_option'],
                             very_good_option=a_new_aspect_dict['very_good_option'],
                             related_melia_aspect=a_new_aspect_dict['related_melia_aspect'],
                             area=area,
                             active=True).save()

    @staticmethod
    def delete_aspects(aspects_to_delete: List[EvaluationAspect]):
        for an_aspect in aspects_to_delete:
            an_aspect.active = False
            an_aspect.save()
