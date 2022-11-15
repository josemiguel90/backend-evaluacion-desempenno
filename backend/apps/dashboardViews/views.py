from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.extraPermissions import IsEvaluatorFromArea
from ..evaluation.models import MonthlyMeliaEvaluation, AnualEvaluation
from ..salesPlan.models import MonthlySalePlan
from ..family.models import Family
from ..sellArea.models import PuntoDeVenta
from ..hotel.models import Hotel
from ..payTime.models import PayTime
from ..payTime.serializers import PayTimeSerializer
from .helpFunctions import buildEval, buildListItemOrder, getGastronomyEvaluationId, getPayTimeId, getPayTimeName


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMainNumbers(request):
    try:
        response = {
            'users': get_user_model().objects.all().count(),
            'salePlans': MonthlySalePlan.objects.all().count(),
            'families': Family.objects.filter(activo=True).count(),
            'salePlaces': PuntoDeVenta.objects.filter(activo=True).count(),
        }
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRangeOfMelyaEvaluations(request):
    try:
        response = {'veryGood': 0, 'good': 0, 'regular': 0, 'bad': 0}
        for evaluation in MonthlyMeliaEvaluation.objects.all():
            if evaluation.totalCalificacion().split('-')[1].lstrip() == 'MB':
                response['veryGood'] += 1
            elif evaluation.totalCalificacion().split('-')[1].lstrip() == 'B':
                response['good'] += 1
            elif evaluation.totalCalificacion().split('-')[1].lstrip() == 'R':
                response['regular'] += 1
            elif evaluation.totalCalificacion().split('-')[1].lstrip() == 'M':
                response['bad'] += 1
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRangeOfAnualEvaluations(request):
    try:
        response = {'veryGood': 0, 'good': 0, 'bad': 0}
        for evaluation in AnualEvaluation.objects.all():
            if evaluation.finalEvaluation == 'Superior':
                response['veryGood'] += 1
            elif evaluation.finalEvaluation == 'Adecuado':
                response['good'] += 1
            elif evaluation.finalEvaluation == 'Deficiente':
                response['bad'] += 1
        return Response(response, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsEvaluatorFromArea])
def getTableEvaluations(request):
    try:
        # Get last 3 Paytimes
        paytimes = list(PayTime.objects.filter(
            isEliminated=False).order_by('-year', '-monthOrder')[0:3])

        # Validate if There is Paytimes
        if len(paytimes) == 0:
            return Response([], status=status.HTTP_200_OK)

        # Build Response
        listToReturn, listToOrder, index = [], [], 0

        for hotel in Hotel.objects.all():
            for worker in hotel.workers.filter(activo=True):
                # BuildEvals
                firstEval = buildEval(1, 0, paytimes, worker)
                secondEval = buildEval(2, 1, paytimes, worker)
                thirdEval = buildEval(3, 2, paytimes, worker)

                # Append new data to list to return
                newItem = {
                    # Worker Data
                    "name": worker.nombreCompleto(),
                    "hotel": hotel.name,
                    # First Eval
                    "firstEvalDate": firstEval['payTimeName'] if firstEval is not None else None,
                    "firstEvalCalification": firstEval['totalCalificacion'] if firstEval is not None else None,
                    "firstEvalTotal": firstEval['totalPoints'] if firstEval is not None else None,
                    "firstcalificacion": firstEval['calificacion'] if firstEval is not None else "No Registrada",
                    # Second Eval
                    "secondEvalDate": secondEval['payTimeName'] if secondEval is not None else None,
                    "secondEvalCalification": secondEval['totalCalificacion'] if secondEval is not None else None,
                    "secondEvalTotal": secondEval['totalPoints'] if secondEval is not None else None,
                    "secondcalificacion": secondEval['calificacion'] if secondEval is not None else "No Registrada",
                    # Second Eval
                    "thirdEvalDate": thirdEval['payTimeName'] if thirdEval is not None else None,
                    "thirdEvalCalification": thirdEval['totalCalificacion'] if thirdEval is not None else None,
                    "thirdEvalTotal": thirdEval['totalPoints'] if thirdEval is not None else None,
                    "thirdcalificacion": thirdEval['calificacion'] if thirdEval is not None else "No Registrada",

                    # IDS
                    "hotelId": hotel.pk,
                    "workerId": worker.pk,
                    # First IDS
                    "firstEvalId": firstEval['id'] if firstEval is not None else None,
                    "firstPayTimeId": getPayTimeId(1, 0, paytimes),
                    "firstPayTimeName": getPayTimeName(1, 0, paytimes),
                    "firstGastronomyId": getGastronomyEvaluationId(firstEval['payTime'] if firstEval is not None else None, worker.pk),
                    "firstMeliaId": firstEval['id'] if firstEval is not None else None,
                    # Second IDS
                    "secondEvalId": secondEval['id'] if secondEval is not None else None,
                    "secondPayTimeId": getPayTimeId(2, 1, paytimes),
                    "secondPayTimeName": getPayTimeName(2, 1, paytimes),
                    "secondGastronomyId": getGastronomyEvaluationId(secondEval['payTime'] if secondEval is not None else None, worker.pk),
                    "secondMeliaId": secondEval['id'] if secondEval is not None else None,
                    # Third IDS
                    "thirdEvalId": thirdEval['id'] if thirdEval is not None else None,
                    "thirdPayTimeId": getPayTimeId(3, 2, paytimes),
                    "thirdPayTimeName": getPayTimeName(3, 2, paytimes),
                    "thirdGastronomyId": getGastronomyEvaluationId(thirdEval['payTime'] if thirdEval is not None else None, worker.pk),
                    "thirdMeliaId": thirdEval['id'] if thirdEval is not None else None,
                }
                listToReturn.append(newItem)

                # Build new List item to Order
                newTuple = []
                buildListItemOrder(newItem, newTuple, "firstEvalTotal")
                buildListItemOrder(newItem, newTuple, "secondEvalTotal")
                buildListItemOrder(newItem, newTuple, "thirdEvalTotal")
                newTuple.append(newItem['name'])
                newTuple.append(newItem['hotel'])
                newTuple.append(index)
                index += 1

                # Add new Item to order to order List
                listToOrder.append(newTuple)
        # Sort Response
        listToOrder.sort()

        # Build Again Response after list ordered

        listResponse = {
            "payTimes": {
                "first": getPayTimeName(1, 0, paytimes),
                "second": getPayTimeName(2, 1, paytimes),
                "third": getPayTimeName(3, 2, paytimes)
            },
            "data": [listToReturn[item[-1]] for item in listToOrder],
        }

        return Response(listResponse, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
