from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.dashboardViews.helpFunctions import buildEval, buildListItemOrder
from apps.evaluation_in_area.models import MonthEvaluation, YearMeliaEvaluation
from apps.evaluation_in_area.util import get_month_evaluation
from apps.hotel.models import Hotel
from apps.payTime.models import PayTime
from backend.extraPermissions import IsEvaluatorFromArea


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_ranges_of_month_melia_evaluations(request):

    response = {'veryGood': 0, 'good': 0, 'regular': 0, 'bad': 0}
    evaluations = MonthEvaluation.objects.filter(evaluation_area=request.user.area)
    for evaluation in evaluations:
        final_melia_note = evaluation.get_melia_final_note()

        if final_melia_note == 'M':
            response['bad'] = response['bad'] + 1

        elif final_melia_note == 'R':
            response['regular'] = response['regular'] + 1

        elif final_melia_note == 'B':
            response['good'] = response['good'] + 1

        elif final_melia_note == 'MB':
            response['veryGood'] = response['veryGood'] + 1

    return Response(response, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_ranges_of_year_melia_evaluations(request):

    response = {'veryGood': 0, 'good': 0, 'bad': 0}
    evaluations = YearMeliaEvaluation.objects.filter(evaluation_area=request.user.area)

    for evaluation in evaluations:

        if evaluation.final_evaluation == YearMeliaEvaluation.DEFICIENT_EVALUATION:
            response['bad'] = response['bad'] + 1

        elif evaluation.final_evaluation == YearMeliaEvaluation.APPROPRIATE_EVALUATION:
            response['good'] = response['good'] + 1

        elif evaluation.final_evaluation == YearMeliaEvaluation.SUPERIOR_EVALUATION:
            response['veryGood'] = response['veryGood'] + 1

    return Response(response, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_last_three_evaluation_periods(request):
    try:

        user_worker = request.user.worker
        area = request.user.area

        # Get last 3 Paytimes
        payment_periods = list(PayTime.objects.filter(
            isEliminated=False).order_by('-year', '-monthOrder')[0:3])

        # Validate if There is Paytimes
        if len(payment_periods) == 0:
            return Response([], status=status.HTTP_200_OK)

        # Build Response
        workers_with_evaluations = []

        first_payment_period = payment_periods[0]
        second_payment_period = payment_periods[1]
        third_payment_period = payment_periods[2]

        for hotel in Hotel.objects.all():
            for worker in hotel.workers.filter(activo=True, area_evaluacion=request.user.area)\
                    .exclude(no_interno=user_worker.no_interno):

                first_eval = get_month_evaluation(first_payment_period, worker, area)
                second_eval = get_month_evaluation(second_payment_period, worker, area)
                third_eval = get_month_evaluation(third_payment_period, worker, area)

                # Append new data to list to return
                current_worker_and_evaluations = {
                    # Worker Data
                    "name": worker.nombreCompleto(),
                    "workerId": worker.no_interno,
                    "hotel": hotel.name,
                    "hotelId": hotel.id,

                    # First Eval
                    "firstEvalId": first_eval.id if first_eval is not None else None,
                    "firstPayTimeId": first_payment_period.id,
                    "firstEvalDate": str(first_payment_period),
                    "firstEvalCalification": first_eval.get_melia_final_note() if first_eval is not None else None,
                    "firstTotal": first_eval.melia_total_points() if first_eval is not None else None,

                    # Second Eval
                    "secondEvalId": second_eval.id if second_eval is not None else None,
                    "secondPayTimeId": second_payment_period.id,
                    "secondEvalDate": str(second_payment_period),
                    "secondEvalCalification": second_eval.get_melia_final_note() if second_eval is not None else None,
                    "secondTotal": second_eval.melia_total_points() if second_eval is not None else None,

                    # Third Eval
                    "thirdEvalId": third_eval.id if third_eval is not None else None,
                    "thirdPayTimeId": third_payment_period.id,
                    "thirdEvalDate": str(third_payment_period),
                    "thirdEvalCalification": third_eval.get_melia_final_note() if third_eval is not None else None,
                    "thirdTotal": third_eval.melia_total_points() if third_eval is not None else None,

                }
                workers_with_evaluations.append(current_worker_and_evaluations)

        listResponse = {
            "payTimes": {
                "first": str(first_payment_period),
                "second": str(second_payment_period),
                "third": str(first_payment_period)
            },
            "data": workers_with_evaluations,
        }

        return Response(listResponse, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
