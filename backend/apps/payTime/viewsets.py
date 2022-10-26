from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import PayTime, PayTimeSerializer
from backend.extraPermissions import IsEvaluatorFromArea
from backend.utils import getDateByStrig, getNoPaytimesList


class PayTimeViewSet(viewsets.ModelViewSet):
    queryset = PayTime.objects.filter(isEliminated=False).order_by('-year', '-monthOrder')
    serializer_class = PayTimeSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    def list(self, request):
        allowEmptyTable = request.query_params.get('allow')
        queryset = PayTime.objects.filter(isEliminated=False).order_by('-year', '-monthOrder')
        if allowEmptyTable is None and queryset.count() == 0:
            return Response({"detail": getNoPaytimesList()}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PayTimeSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def deleteSelectedItems(self, request):
        try:
            for payTime in request.data:
                pt = PayTime.objects.get(id=int(payTime.get('id')))
                pt.isEliminated = True
                pt.save()
            return Response({'Pay times deleted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def importSelectedItems(self, request):
        try:
            for payTime in request.data:
                if PayTime.objects.filter(id=payTime.get('id_peri')).exists():
                    pt = PayTime.objects.get(id=payTime.get('id_peri'))
                    pt.isEliminated = False
                    pt.month = payTime.get('nombre')
                    pt.initialDate = getDateByStrig(payTime.get('fecha_inicio'))
                    pt.endDate = getDateByStrig(payTime.get('fecha_fin'))
                    pt.monthOrder = payTime.get('orden')
                    pt.year = payTime.get('ejercicio')
                    pt.save()
                else:
                    PayTime.objects.create(
                        id=payTime.get('id_peri'),
                        month=payTime.get('nombre'),
                        initialDate=getDateByStrig(payTime.get('fecha_inicio')),
                        endDate=getDateByStrig(payTime.get('fecha_fin')),
                        monthOrder=payTime.get('orden'),
                        year=payTime.get('ejercicio'),
                        isEliminated=False
                    )
            return Response({'Pay times imported'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def rebuildList(self, request):
        try:
            for payTime in request.data:
                myPayTime = PayTime.objects.get(id=payTime.get('id'))
                if 'hasToRemove' in payTime:
                    myPayTime.isEliminated = True
                    myPayTime.save()
                else:
                    myPayTime.month = payTime.get('month')
                    myPayTime.monthOrder = payTime.get('monthOrder')
                    myPayTime.initialDate = getDateByStrig(payTime.get('initialDate'))
                    myPayTime.endDate = getDateByStrig(payTime.get('endDate'))
                    myPayTime.year = payTime.get('year')
                    myPayTime.save()
            return Response({'Pay times rebuilded'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
