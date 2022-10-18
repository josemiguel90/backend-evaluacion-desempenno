from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.evaluation_in_area.models import EvaluationAspect, MeliaAspect, EvaluationArea
from apps.evaluation_in_area.serializers.evaluation_aspect import EvaluationAspectSerializer
from backend.extraPermissions import IsEvaluatorFromArea


class EvaluationAspectViewSet(ModelViewSet):

    queryset = EvaluationAspect.objects
    serializer_class = EvaluationAspectSerializer
    permission_classes = [IsEvaluatorFromArea]

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            related_melia_aspect = MeliaAspect.objects.get(pk=data.get('related_melia_aspect'))
            area = EvaluationArea.objects.get(pk=data.get('area'))

            aspect = EvaluationAspect(
                name=data.get('name'),
                bad_option=data.get('bad_option'),
                regular_option=data.get('regular_option'),
                good_option=data.get('good_option'),
                very_good_option=data.get('very_good_option'),
                type=data.get('type'),
                related_melia_aspect=related_melia_aspect,
                area=area,
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
