import datetime
from typing import List
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.evaluation_in_area.models import MonthEvaluation, MonthEvaluationAspectValue
from apps.evaluation_in_area.serializers.month_evaluation import MonthEvaluationSerializer, \
    SimpleMonthEvaluationSerializer
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

            month_evaluation = MonthEvaluation(evaluation_area=request.user.area,
                                               date=datetime.date.today(),
                                               worker=worker,
                                               worker_charge=worker.cargo,
                                               evaluator=f'{evaluator.first_name} {evaluator.last_name}',
                                               evaluator_charge=evaluator.area.boss_charge,
                                               payment_period=payment_period)
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
