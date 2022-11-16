from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from apps.evaluation_in_area.models import YearMeliaEvaluation
from apps.evaluation_in_area.serializers.year_evaluation import YearMeliaEvaluationSerializer, \
    SimpleYearMeliaEvaluationSerializer
from apps.workers.models import Worker
from backend.extraPermissions import IsEvaluatorFromArea


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def list_year_evaluations(request, year):
    evaluations_in_year = YearMeliaEvaluation.objects.filter(year=year,
                                                             evaluation_area=request.user.area)
    serializer = SimpleYearMeliaEvaluationSerializer(evaluations_in_year, many=True)

    return Response(serializer.data, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsEvaluatorFromArea])
def get_year_evaluation_by_id(request, evaluation_id):
    try:
        evaluation = YearMeliaEvaluation.objects.filter(evaluation_area=request.user.area) \
            .get(id=evaluation_id)

        serializer = YearMeliaEvaluationSerializer(evaluation)
        return Response(serializer.data, status.HTTP_200_OK)

    except YearMeliaEvaluation.DoesNotExist:
        return Response(f'No existe la evaluación anual con id {evaluation_id}')


@api_view(['POST'])
@permission_classes([IsEvaluatorFromArea])
def create_year_evaluation(request):
    data = request.data
    try:
        worker = Worker.objects.filter(activo=True, area_evaluacion=request.user.area) \
            .get(no_interno=data['workerInternNumber'])

        evaluation = YearMeliaEvaluation(
            year=data['year'],
            worker=worker,
            worker_charge=worker.cargo,
            evaluator=request.user.worker,
            evaluator_charge=request.user.worker.cargo,
            evaluation_area=request.user.area,
            summary=data['summary'],
            fulfillment=data['fulfillment'],
            behavior=data['behavior'],
            use_and_care=data['useAndCare'],
            recommendation=data['recommendation'],
            final_evaluation=data['finalEvaluation']
        )
        evaluation.save()
        serializer = YearMeliaEvaluationSerializer(evaluation)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Worker.DoesNotExist:
        return Response(f'No existe el trabajador con número de interno {data["workerInternNumber"]}',
                        status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response(e.args[0], status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsEvaluatorFromArea])
def update_year_evaluation(request, evaluation_id):
    data = request.data
    try:
        evaluation = YearMeliaEvaluation.objects.filter(evaluation_area=request.user.area) \
            .get(id=evaluation_id)
        evaluation.summary = data.get('summary')
        evaluation.fulfillment = data.get('fulfillment')
        evaluation.behavior = data.get('behavior')
        evaluation.use_and_care = data.get('useAndCare')
        evaluation.recommendation = data.get('recommendation')
        evaluation.final_evaluation = data.get('finalEvaluation')
        evaluation.save()

        serializer = YearMeliaEvaluationSerializer(evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except YearMeliaEvaluation.DoesNotExist:
        return Response(f'No existe la evaluación anual con id {evaluation_id}')

    except Exception as e:
        return Response(e.args[0], status.HTTP_500_INTERNAL_SERVER_ERROR)
