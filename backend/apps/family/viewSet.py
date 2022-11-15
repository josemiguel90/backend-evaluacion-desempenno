from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.extraPermissions import IsEvaluatorFromArea
from backend.utils import getFamilyDeleteError
from .serializers import FamilySerializer, Family


class FamilyViewSet(viewsets.ModelViewSet):
    queryset = Family.objects.filter(activo=True)
    serializer_class = FamilySerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def updateFamilies(self, request):
        try:
            for family in request.data:
                if Family.objects.filter(cod_grupo=family.get('cod_grupo')).exists():
                    existingFamily = Family.objects.get(cod_grupo=family.get('cod_grupo'))
                    existingFamily.cod_grupo = family.get('cod_grupo')
                    existingFamily.desc_grupo = family.get('desc_grupo')
                    existingFamily.activo = family.get('activo')
                    existingFamily.save()
                else:
                    Family.objects.create(
                        id_grupo=family.get('id_grupo'),
                        cod_grupo=family.get('cod_grupo'),
                        desc_grupo=family.get('desc_grupo'),
                        activo=family.get('activo')
                    )
            return Response({'Families Updated Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteSelectedFamilies(self, request):
        try:
            for family in request.data:
                fam = Family.objects.get(cod_grupo=family.get('cod_grupo'))
                fam.activo = False
                fam.save()
            return Response({'Families Eliminated Successfully'}, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({'detail': getFamilyDeleteError()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def sincronizeFamilies(self, request):
        try:
            data = request.data
            myFamilies = data.get('myFamilies')
            zunPosFamilies = data.get('zunPosFamilies')
            for myFamily in myFamilies:
                exist = False
                family = Family.objects.get(id_grupo=myFamily.get('id_grupo'))
                for zunPosFam in zunPosFamilies:
                    if family.id_grupo == zunPosFam.get('id_grupo'):
                        exist = True
                        family.cod_grupo = zunPosFam.get('cod_grupo')
                        family.desc_grupo = zunPosFam.get('desc_grupo')
                        family.activo = zunPosFam.get('activo')
                        family.save()
                        break
                if not exist:
                    family.activo = False
                    family.save()
            return Response({'Families Sincronized Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
