import datetime
from typing import List

from django.views.generic import detail
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue
from apps.evaluation_in_area.serializers.month_evaluation import MonthEvaluationSerializer, \
    SimpleMonthEvaluationSerializer
from apps.evaluation_in_area.util import find_aspect_with_id_in_list, \
    find_month_evaluation_for_worker_and_payment_period
from apps.payTime.models import PayTime
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

            # La evaluación podía existir desde antes en la base de datos
            # si no había sido eliminada completamente
            month_evaluation = find_month_evaluation_for_worker_and_payment_period(
                request.user, worker, payment_period)

            if month_evaluation is None:
                month_evaluation = MonthEvaluation(evaluation_area=request.user.area,
                                                   date=datetime.date.today(),
                                                   worker=worker,
                                                   worker_charge=worker.cargo,
                                                   evaluator=f'{evaluator.first_name} {evaluator.last_name}',
                                                   evaluator_charge=evaluator.area.boss_charge,
                                                   payment_period=payment_period)
            else:
                month_evaluation.are_evaluated_aspects_deleted = False
                month_evaluation.date = datetime.date.today()
                month_evaluation.worker_charge = worker.cargo
                month_evaluation.evaluator = f'{evaluator.first_name} {evaluator.last_name}'
                month_evaluation.evaluator_charge = evaluator.area.boss_charge

            month_evaluation.save()

            for an_evaluation in evaluations:
                an_evaluated_aspect = MonthEvaluationAspectValue(month_evaluation=month_evaluation,
                                                                 aspect_id=an_evaluation['id'],
                                                                 assigned_value=an_evaluation['value'])
                an_evaluated_aspect.save()

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


@api_view(['DELETE'])
@permission_classes([IsEvaluatorFromArea])
def undo_month_area_evaluation(request, month_evaluation_id):
    try:
        month_evaluation = MonthEvaluation.objects.filter(evaluation_area=request.user.area)\
            .filter(are_evaluated_aspects_deleted=False).get(id=month_evaluation_id)

        MonthEvaluationAspectValue.objects.filter(month_evaluation=month_evaluation)\
            .delete()

        month_evaluation.are_evaluated_aspects_deleted = True
        month_evaluation.save()

        # Si ya estaba eliminada la evaluación de Meliá, entonces eliminar el objeto
        # de la base de datos
        if month_evaluation.are_evaluated_melia_aspects_deleted:
            month_evaluation.delete()

        return Response(status=status.HTTP_200_OK)

    except MonthEvaluation.DoesNotExist:
        return Response({'detail': f'La evaluación mensual con id {month_evaluation_id} no existe'},
                        status.HTTP_404_NOT_FOUND)
