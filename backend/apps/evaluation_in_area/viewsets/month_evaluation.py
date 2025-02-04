import datetime
from functools import reduce
from statistics import mean
from typing import List

from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue, MeliaAspect, EvaluationAspect, \
    MeliaMonthEvaluationAspectValue
from apps.evaluation_in_area.serializers.melia_aspect import MeliaAspectSerializer
from apps.evaluation_in_area.serializers.month_evaluation import MonthEvaluationSerializer, \
    SimpleMonthEvaluationSerializer
from apps.evaluation_in_area.util import find_aspect_with_id_in_list, \
    find_month_evaluation_for_worker_and_payment_period
from apps.hotel.models import Hotel
from apps.hotel.serializers import HotelSerializer
from apps.payTime.models import PayTime
from apps.payTime.serializers import PayTimeSerializer
from apps.users.models import User
from apps.workers.models import Worker
from backend.extraPermissions import IsEvaluatorFromArea


class MonthEvaluationViewSet(ViewSet):

    queryset = MonthEvaluation.objects.all()
    permission_classes = [IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'], url_path='area')
    def create_month_evaluation(self, request):
        worker_intern_number = request.data['workerInternNumber']
        payment_period_id = request.data['paymentPeriodId']
        evaluations: List[dict] = request.data['evaluations']

        try:
            worker = Worker.objects.filter(area_evaluacion=request.user.area).get(no_interno=worker_intern_number)
            evaluator: User = request.user
            payment_period = PayTime.objects.get(id=payment_period_id)

            month_evaluation = MonthEvaluation(evaluation_area=request.user.area,
                                               date=datetime.date.today(),
                                               worker=worker,
                                               worker_charge=worker.cargo,
                                               evaluator=request.user.worker,
                                               evaluator_charge=evaluator.area.boss_charge,
                                               payment_period=payment_period)
            month_evaluation.save()

            # Dar puntuaciones a la evaluación mensual del área
            for an_evaluation in evaluations:
                an_evaluated_aspect = MonthEvaluationAspectValue(month_evaluation=month_evaluation,
                                                                 aspect_id=an_evaluation['id'],
                                                                 assigned_value=an_evaluation['value'])
                an_evaluated_aspect.save()

            # Derivar la evaluación mensual de Meliá
            aspect_ids = list(map(lambda an_evaluation: an_evaluation['id'], evaluations))
            area_aspects_used_in_this_evaluation = EvaluationAspect.objects.filter(id__in=aspect_ids)

            for a_melia_aspect in MeliaAspect.objects.filter(is_active=True):
                area_aspects_related_to_a_melia_aspect = area_aspects_used_in_this_evaluation \
                    .filter(related_melia_aspect=a_melia_aspect)

                related_aspects_ids = area_aspects_related_to_a_melia_aspect.values_list('id', flat=True)

                assigned_values = [an_evaluation['value'] for an_evaluation in evaluations
                                   if an_evaluation['id'] in related_aspects_ids]

                value_for_melia_aspect = round(mean(assigned_values))
                MeliaMonthEvaluationAspectValue(
                    month_evaluation=month_evaluation,
                    melia_aspect=a_melia_aspect,
                    assigned_value=value_for_melia_aspect).save()

            return Response(status=status.HTTP_200_OK)

        except Worker.DoesNotExist:
            return Response({'detail': f'El trabajador con número de interno {request.data["workerInternNumber"]}'
                                       f'no existe'}, status.HTTP_404_NOT_FOUND)

        except PayTime.DoesNotExist:
            return Response({'detail': f'El período de pago con id {request.data["payTimePeriodId"]} no existe'},
                            status.HTTP_404_NOT_FOUND)

        except Exception as e:
            raise e


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_month_evaluation_by_id(request, month_evaluation_id):
    try:
        evaluation = MonthEvaluation.objects.filter(evaluation_area=request.user.area).get(id=month_evaluation_id)
        serializer = MonthEvaluationSerializer(evaluation)

        return Response(serializer.data, status.HTTP_200_OK)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'La evaluación mensual con id {month_evaluation_id} no existe'},
                        status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_area_evaluation_given_worker_and_payment_period(request, payment_period_id, worker_intern_number):

    try:
        worker = Worker.objects.filter(area_evaluacion=request.user.area).get(no_interno=worker_intern_number)
        payment_period = PayTime.objects.get(id=payment_period_id)

        month_evaluation = MonthEvaluation.objects.get(
            evaluation_area=request.user.area,
            worker=worker,
            payment_period=payment_period
        )
        month_evaluation_serializer = MonthEvaluationSerializer(month_evaluation)

        return Response(month_evaluation_serializer.data, status.HTTP_200_OK)

    except Worker.DoesNotExist:
        return Response({'detail': f'El trabajador con número de interno {worker_intern_number}'
                                   f'no existe en esta área.'}, status.HTTP_404_NOT_FOUND)

    except PayTime.DoesNotExist:
        return Response({'detail': f'El período de pago con id {payment_period_id} no existe'},
                        status.HTTP_404_NOT_FOUND)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'No se encontró la evaluación mensual realizada al trabajador'
                                   f'con número de interno {worker_intern_number} en el Período'
                                   f'de Pago con id {payment_period_id}'}, status.HTTP_404_NOT_FOUND)

    except Exception as e:
        raise e


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_evaluations_in_area_and_payment_period(request, hotel_id, payment_period_id):
    try:
        payment_period = PayTime.objects.get(id=payment_period_id)
        evaluations = MonthEvaluation.objects.filter(evaluation_area=request.user.area,
                                                     payment_period_id=payment_period,
                                                     worker__unidad_org_id=hotel_id)

        evaluation_serializer = SimpleMonthEvaluationSerializer(evaluations, many=True)
        return Response(evaluation_serializer.data, status.HTTP_200_OK)

    except PayTime.DoesNotExist:
        return Response({'detail': f'No existe el período de pago con id {payment_period_id}'},
                        status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsEvaluatorFromArea])
def update_month_evaluation(request, month_evaluation_id: int):
    updated_aspects_with_values: list = request.data

    try:
        month_evaluation = MonthEvaluation.objects.filter(evaluation_area=request.user.area)\
            .get(id=month_evaluation_id)

        month_evaluation_aspect_values = MonthEvaluationAspectValue.objects.filter(month_evaluation=month_evaluation_id)

        for a_month_evaluation_aspect_value in month_evaluation_aspect_values:
            updated_aspect_from_request = find_aspect_with_id_in_list(a_month_evaluation_aspect_value.aspect_id,
                                                                      updated_aspects_with_values)
            a_month_evaluation_aspect_value.assigned_value = updated_aspect_from_request['value']
            a_month_evaluation_aspect_value.save()

        serializer = MonthEvaluationSerializer(month_evaluation)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'La evaluación mensual con id {month_evaluation_id} no existe'})


@api_view(['PUT'])
@permission_classes([IsEvaluatorFromArea])
def update_melia_values_and_observations_month_evaluation(request, month_evaluation_id):
    updated_melia_aspects_with_value: list = request.data['aspectsWithValue']


    try:
        month_evaluation = MonthEvaluation.objects.filter(evaluation_area=request.user.area) \
            .get(id=month_evaluation_id)
        month_evaluation.melia_observations = request.data['observations']
        month_evaluation.save()

        melia_aspects_with_old_values = MeliaMonthEvaluationAspectValue.objects \
            .filter(month_evaluation=month_evaluation)

        for a_melia_aspect_with_value in melia_aspects_with_old_values:
            melia_aspect_with_new_value = find_aspect_with_id_in_list(a_melia_aspect_with_value.melia_aspect.id,
                                                                      updated_melia_aspects_with_value)
            a_melia_aspect_with_value.assigned_value = melia_aspect_with_new_value['value']
            a_melia_aspect_with_value.save()

        serializer = MonthEvaluationSerializer(month_evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'La evaluación mensual con id {month_evaluation_id} no existe'},
                        status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsEvaluatorFromArea])
def undo_month_area_evaluation(request, month_evaluation_id):
    try:
        month_evaluation = MonthEvaluation.objects.filter(evaluation_area=request.user.area)\
            .get(id=month_evaluation_id)

        # Se eliminarán los valores otorgados a los aspectos de la evaluación
        # mensual y los de meliá
        month_evaluation.delete()

        return Response(status=status.HTTP_200_OK)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'La evaluación mensual con id {month_evaluation_id} no existe'},
                        status.HTTP_404_NOT_FOUND)


def calculate_discount(totalPoints):
    # {puntos totales : descuento recibido}
    values = {14: 50, 15: 53, 16: 57, 17: 61, 18: 65, 19: 69, 20: 73, 21: 75, 22: 79, 23: 83, 24: 87, 25: 91,
              26: 95, 27: 99}
    if totalPoints in values:
        return 100 - values[totalPoints]
    return 0


def calculate_total_points(aspects_with_value):
    total = 0
    for an_aspect in aspects_with_value:
        total += an_aspect.assigned_value
    return total


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_month_performance(request, hotel_id, payment_period_id):
    """Devuelve el desempeño mensual de los trbajadores evaluados"""
    melia_aspects = MeliaAspect.objects.all().order_by('order')
    workers = Worker.objects.filter(activo=True,
                                    area_evaluacion=request.user.area,
                                    unidad_org__id=hotel_id)
    payment_period = PayTime.objects.get(id=payment_period_id)
    hotel = Hotel.objects.get(id=hotel_id)

    workers_with_performance = []

    for a_worker in workers:
        evaluation = MonthEvaluation.objects.filter(
            worker__no_interno=a_worker.no_interno,
            evaluation_area=request.user.area,
            payment_period__id=payment_period_id).first()

        if evaluation is not None:
            aspects_with_values = MeliaMonthEvaluationAspectValue.objects.filter(month_evaluation=evaluation)\
                .order_by('melia_aspect__order')
            total_points = calculate_total_points(aspects_with_values)
            discount = calculate_discount(total_points)
            values = list(aspects_with_values.values_list('assigned_value', flat=True))
            worker_performance = {'workerName': a_worker.nombreCompleto(),
                                  'workerId': a_worker.no_interno,
                                  'totalPoints': total_points,
                                  'values': values,
                                  'discount': discount}
            workers_with_performance.append(worker_performance)

    return Response({'meliaAspects': MeliaAspectSerializer(melia_aspects, many=True).data,
                     'paymentPeriod': PayTimeSerializer(payment_period).data,
                     'hotel': HotelSerializer(hotel).data,
                     'workerPerformances': workers_with_performance})
