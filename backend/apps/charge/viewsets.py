from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.utils import getCategoryNoExistError
from .serializers import Charge, ChargeSerializer
from ..category.models import OccupationalCategory


class ChargeViewSet(viewsets.ModelViewSet):
    queryset = Charge.objects.filter(activo=True)
    serializer_class = ChargeSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'])
    def rebuildList(self, request):
        try:
            newCharges = request.data
            for charge in newCharges:
                if Charge.objects.filter(pk=charge['id_cargos']).exists():
                    ch = Charge.objects.get(pk=charge['id_cargos'])
                    ch.cod_cargo = charge['cod_cargo']
                    ch.descripcion = charge['descripcion']
                    ch.activo = True
                    ch.fk_cat_ocupacion = OccupationalCategory.objects.get(pk=charge['fk_cat_ocupacion'])
                    ch.save()
                else:
                    Charge.objects.create(
                        id_cargos=charge['id_cargos'],
                        cod_cargo=charge['cod_cargo'],
                        descripcion=charge['descripcion'],
                        activo=True,
                        fk_cat_ocupacion=OccupationalCategory.objects.get(pk=charge['fk_cat_ocupacion']),
                    )
            for charge in Charge.objects.all():
                exist = False
                for i in newCharges:
                    if charge.pk == i['id_cargos']:
                        exist = True
                        break
                if not exist:
                    charge.activo = False
                    charge.save()
            return Response({'List rebuilded successfully'}, status=status.HTTP_200_OK)
        except OccupationalCategory.DoesNotExist:
            return Response({'detail': getCategoryNoExistError()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
