from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.evaluation.serializers.monthlyMeliaEvaluationSerliazer import MonthlyMeliaEvaluationSerliazer
from apps.hotel.models import Hotel
from backend.extraPermissions import IsEvaluatorFromArea
from apps.evaluation.models import MonthlyGastronomyEvaluation, MonthlyMeliaEvaluation
from apps.payTime.models import PayTime
from apps.workers.models import Worker
from backend.utils import insertion_sort


def getGastronomyEvaluationOnPayTime(pay_time: PayTime, worker: Worker):
    if MonthlyGastronomyEvaluation.objects.filter(payTime__id=pay_time.id,
                                                  evaluateWorker__no_interno=worker.no_interno).exists():
        model = MonthlyGastronomyEvaluation.objects.get(payTime__id=pay_time.id,
                                                        evaluateWorker__no_interno=worker.no_interno)
        return model.id
    return None


def getMeliaEvaluationOnPayTime(pay_time: PayTime, worker: Worker):
    if MonthlyMeliaEvaluation.objects.filter(payTime__id=pay_time.id,
                                             evaluateWorker__no_interno=worker.no_interno).exists():
        model = MonthlyMeliaEvaluation.objects.get(payTime__id=pay_time.id,
                                                   evaluateWorker__no_interno=worker.no_interno)
        return model.id
    return None


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsEvaluatorFromArea])
def getMonthlyPerformanceEvaluationReport(request):
    data = request.data
    try:
        hotel = Hotel.objects.get(pk=int(data.get('hotelId')))
        payTime = PayTime.objects.get(pk=int(data.get('payTimeId')))
        listToOrder, listNone = [], []
        for worker in hotel.workers.filter(activo=True):
            evalId = getMeliaEvaluationOnPayTime(payTime, worker)
            meliaEvaluation = None if evalId is None else MonthlyMeliaEvaluation.objects.get(pk=evalId)
            serializer = None if evalId is None else MonthlyMeliaEvaluationSerliazer(meliaEvaluation, many=False).data
            newItem = {
                'worker': str(worker.nombreCompleto()).title(),
                'meliaEvaluation': serializer,
                'total': None if meliaEvaluation is None else meliaEvaluation.totalPoints(),
                'discount': None if meliaEvaluation is None else meliaEvaluation.getDisscount(),
            }
            if newItem['meliaEvaluation'] is None:
                listNone.append(newItem)
            else:
                listToOrder.append(newItem)
        insertion_sort(listToOrder)
        listToReturn = listToOrder + listNone
        return Response(listToReturn, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
