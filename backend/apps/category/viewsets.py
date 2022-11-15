from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from backend.extraPermissions import IsEvaluatorFromArea
from .serializers import OccupationalCategory, OccupationalCategoryMiniSerializer, OccupationalCategorySerializer


class OccupationalCategoryViewSet(viewsets.ModelViewSet):
    queryset = OccupationalCategory.objects.filter(activo=True)
    serializer_class = OccupationalCategoryMiniSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    def retrieve(self, request, *args, **kwargs):
        return Response(OccupationalCategorySerializer(self.get_object(), many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def rebuildList(self, request):
        try:
            newCategories = request.data
            for cat in newCategories:
                if OccupationalCategory.objects.filter(pk=cat['id_categ']).exists():
                    oc = OccupationalCategory.objects.get(pk=cat['id_categ'])
                    oc.cod_categ = cat['cod_categ']
                    oc.descripcion = cat['descripcion']
                    oc.activo = True
                    oc.save()
                else:
                    OccupationalCategory.objects.create(
                        id_categ=cat['id_categ'],
                        cod_categ=cat['cod_categ'],
                        descripcion=cat['descripcion'],
                        activo=True
                    )
            for cat in OccupationalCategory.objects.all():
                exist = False
                for i in newCategories:
                    if cat.pk == i['id_categ']:
                        exist = True
                        break
                if not exist:
                    cat.activo = False
                    cat.save()
            return Response({'List rebuilded successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
