from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..serializers.monthlyMeliaEvaluationSerliazer import MonthlyMeliaEvaluation, MonthlyMeliaEvaluationSerliazer
from backend.extraPermissions import IsEvaluatorFromArea
from ..views import getMeliaEvaluationOnPayTime, getGastronomyEvaluationOnPayTime
from ...hotel.models import Hotel
from ...payTime.models import PayTime
from ...workers.models import Worker


class MonthlyMeliaEvaluationViewSet(viewsets.ModelViewSet):
    queryset = MonthlyMeliaEvaluation.objects.all()
    serializer_class = MonthlyMeliaEvaluationSerliazer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def getWorkersMonthlyEvaluationByHotelAndPayTime(self, request):
        data = request.data
        try:
            hotel = Hotel.objects.get(pk=int(data.get('hotelId')))
            payTime = PayTime.objects.get(pk=int(data.get('payTimeId')))
            listToReturn = [
                {
                    'hotelId': hotel.id,
                    'payTimeId': payTime.id,
                    'no_interno': worker.no_interno,
                    'fullName': worker.nombreCompleto(),
                    'monthlyMeliaEvaluation': getMeliaEvaluationOnPayTime(payTime, worker),
                    'monthlyGastronomyEvaluation': getGastronomyEvaluationOnPayTime(payTime, worker)
                } for worker in hotel.workers.filter(activo=True)
            ]
            return Response(listToReturn, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PUT'])
    def editEvaluation(self, request):
        data = request.data
        try:
            payTime = PayTime.objects.get(id=int(data.get('payTimeId')))
            evaluateWorker = Worker.objects.get(no_interno=data.get('evaluateWorkerId'))
            evaluatorWorker = Worker.objects.get(no_interno=data.get('evaluatorWorkerId'))
            evaluations = data.get('evaluations')
            monthlyMeliaEval = MonthlyMeliaEvaluation.objects.get(pk=int(data.get('meliaEvaluationId')))
            monthlyMeliaEval.payTime = payTime
            monthlyMeliaEval.evaluateWorker = evaluateWorker
            monthlyMeliaEval.evaluateWorkerCharge = evaluateWorker.cargo
            monthlyMeliaEval.evaluatorWorker = evaluatorWorker
            monthlyMeliaEval.evaluatorWorkerCharge = evaluatorWorker.cargo
            monthlyMeliaEval.asist_punt = evaluations[0].get('points')
            monthlyMeliaEval.dom_cum_tars = evaluations[1].get('points')
            monthlyMeliaEval.trab_equipo = evaluations[2].get('points')
            monthlyMeliaEval.cal_aten_cliente = evaluations[3].get('points')
            monthlyMeliaEval.cui_area_rec_medios = evaluations[4].get('points')
            monthlyMeliaEval.cump_normas = evaluations[5].get('points')
            monthlyMeliaEval.cap_camb_ini_int = evaluations[6].get('points')
            monthlyMeliaEval.observations = data.get('observations')
            monthlyMeliaEval.save()
            return Response({'Monthly Melia Evaluation Edited'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
