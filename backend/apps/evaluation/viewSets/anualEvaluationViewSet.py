from rest_framework import viewsets
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from backend.extraPermissions import IsEvaluatorFromArea
from ..serializers.anualSerializer import AnualEvaluation, AnualEvaluationSerializer
from ...hotel.models import Hotel
from ...workers.models import Worker

from backend.utils import getNoWorkersForEvaluationError


def getAnualEvaluationId(worker_id: str, year: int) -> AnualEvaluation or None:
    if AnualEvaluation.objects.filter(evaluateWorker__no_interno=worker_id, year=year).exists():
        return AnualEvaluation.objects.get(evaluateWorker__no_interno=worker_id, year=year).id
    return None


class AnualEvaluationViewSet(viewsets.ModelViewSet):
    queryset = AnualEvaluation.objects.all().order_by('-year')
    serializer_class = AnualEvaluationSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def getAnualEvaluationsByYearAndHotel(self, request):
        data = request.data
        try:
            hotel = Hotel.objects.get(pk=int(data.get('hotelId')))
            year = data.get('newYear')
            listToReturn = []
            for worker in hotel.workers.filter(activo=True):
                evId = getAnualEvaluationId(worker.no_interno, year)
                item = {
                    'year': year,
                    'hotelId': hotel.id,
                    'workerId': worker.no_interno,
                    'worker': worker.nombreCompleto(),
                    'anualEvaluation': evId,
                    'evaluated': 'No Evaluado' if evId is None else AnualEvaluation.objects.get(id=evId).finalEvaluation
                }
                listToReturn.append(item)
            if len(listToReturn) == 0:
                raise Exception(getNoWorkersForEvaluationError())
            return Response(listToReturn, status=HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def createEvaluation(self, request):
        data = request.data
        try:
            worker = Worker.objects.get(no_interno=data.get('workerId'))
            values = data.get('values')
            AnualEvaluation.objects.create(
                year=int(data.get('year')),
                evaluateWorker=worker,
                evaluateCharge=worker.cargo,
                ind1_resume=values.get('resumen'),
                ind2_cumpl=values.get('cumplimiento'),
                ind3_comport=values.get('comportamiento'),
                ind4_uso_cuid=values.get('usoYCuidado'),
                ind5_recomend=values.get('recomendaciones'),
                finalEvaluation=values.get('evaluacionFinal')
            )
            return Response({'Evaluation Created Successfully'}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def editEvaluation(self, request):
        data = request.data
        try:
            evaluation = AnualEvaluation.objects.get(
                pk=int(data.get('evaluationId')))
            worker = Worker.objects.get(no_interno=data.get('workerId'))
            values = data.get('values')
            evaluation.year = int(data.get('year'))
            evaluation.evaluateWorker = worker
            evaluation.evaluateCharge = worker.cargo
            evaluation.ind1_resume = values.get('resumen')
            evaluation.ind2_cumpl = values.get('cumplimiento')
            evaluation.ind3_comport = values.get('comportamiento')
            evaluation.ind4_uso_cuid = values.get('usoYCuidado')
            evaluation.ind5_recomend = values.get('recomendaciones')
            evaluation.finalEvaluation = values.get('evaluacionFinal')
            evaluation.save()
            return Response({'Evaluation Created Successfully'}, status=HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=HTTP_400_BAD_REQUEST)
