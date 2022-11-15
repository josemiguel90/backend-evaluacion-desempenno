from ..serializers.monthlyGastronomySerializer import MonthlyGastronomyEvaluationSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models import MonthlyGastronomyEvaluation, MonthlyMeliaEvaluation
from backend.extraPermissions import IsEvaluatorFromArea
from ...payTime.models import PayTime
from ...workers.models import Worker


def getMaxEval(indicators: []) -> int:
    indicators.sort()
    indicators.reverse()
    count, bigger = 0, 0
    for i in indicators:
        if indicators.count(i) > count:
            count = indicators.count(i)
            bigger = i
    return bigger


class MonthlyGastronomyEvaluationViewSet(viewsets.ModelViewSet):
    queryset = MonthlyGastronomyEvaluation.objects.all()
    serializer_class = MonthlyGastronomyEvaluationSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def createMonthlyGastronomyEvaluation(self, request):
        data = request.data
        try:
            # Create Gastronomy Evaluation
            payTime = PayTime.objects.get(id=int(data.get('payTimeId')))
            evaluateWorker = Worker.objects.get(no_interno=data.get('evaluateWorkerId'))
            evaluatorWorker = Worker.objects.get(no_interno=data.get('evaluatorWorkerId'))
            evaluations = data.get('evaluations')
            e = MonthlyGastronomyEvaluation.objects.create(
                payTime=payTime,
                evaluateWorker=evaluateWorker,
                evaluateWorkerCharge=evaluateWorker.cargo,
                evaluatorWorker=evaluatorWorker,
                evaluatorWorkerCharge=evaluatorWorker.cargo,
                ind1_CDRI=evaluations[0].get('points'),
                ind2_AMD=evaluations[1].get('points'),
                ind3_PAPPI=evaluations[2].get('points'),
                ind4_CEDP=evaluations[3].get('points'),
                ind5_ROCR=evaluations[4].get('points'),
                ind6_PCRBBRC=evaluations[5].get('points'),
                ind7_CNPE=evaluations[6].get('points'),
                ind8_CCPC=evaluations[7].get('points'),
                ind9_NSC=evaluations[8].get('points'),
                ind10_CPI=evaluations[9].get('points'),
                ind11_INI=evaluations[10].get('points'),
                ind12_RAP=evaluations[11].get('points'),
                ind13_GV=evaluations[12].get('points'),
                ind14_DF=evaluations[13].get('points'),
                ind15_CTP=evaluations[14].get('points'),
                ind16_AC=evaluations[15].get('points'),
                ind17_DIS=evaluations[16].get('points'),
                ind18_CDPA=evaluations[17].get('points'),
                ind19_CTA=evaluations[18].get('points'),
                ind20_HOPT=evaluations[19].get('points'),
                ind21_CNSS=evaluations[20].get('points'),
                ind22_UIE=evaluations[21].get('points'),
                ind23_LCH=evaluations[22].get('points'),
                ind24_APAT=evaluations[23].get('points'),
                ind25_UCU=evaluations[24].get('points'),
            )

            # Create Melia Evaluation from Gastronomy Evaluation
            MonthlyMeliaEvaluation.objects.create(
                payTime=payTime,
                evaluateWorker=evaluateWorker,
                evaluateWorkerCharge=evaluateWorker.cargo,
                evaluatorWorker=evaluatorWorker,
                evaluatorWorkerCharge=evaluatorWorker.cargo,
                asist_punt=getMaxEval([e.ind1_CDRI, e.ind2_AMD, e.ind24_APAT]),
                dom_cum_tars=getMaxEval([e.ind10_CPI, e.ind13_GV, e.ind14_DF, e.ind15_CTP, e.ind19_CTA]),
                trab_equipo=getMaxEval([e.ind3_PAPPI, e.ind17_DIS, e.ind18_CDPA]),
                cal_aten_cliente=getMaxEval(
                    [e.ind8_CCPC, e.ind9_NSC, e.ind16_AC, e.ind20_HOPT, e.ind21_CNSS, e.ind22_UIE, e.ind23_LCH]
                ),
                cui_area_rec_medios=getMaxEval([e.ind5_ROCR, e.ind6_PCRBBRC]),
                cump_normas=getMaxEval([e.ind4_CEDP, e.ind7_CNPE, e.ind25_UCU]),
                cap_camb_ini_int=getMaxEval([e.ind11_INI, e.ind12_RAP]),
                observations=''
            )
            return Response({'Monthly Gastronomy Evaluation Created'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['PUT'])
    def editMonthlyGastronomyEvaluation(self, request):
        data = request.data
        try:
            monthlyEval = MonthlyGastronomyEvaluation.objects.get(pk=int(data.get('evalId')))
            payTime = PayTime.objects.get(id=int(data.get('payTimeId')))
            evaluateWorker = Worker.objects.get(no_interno=data.get('evaluateWorkerId'))
            evaluatorWorker = Worker.objects.get(no_interno=data.get('evaluatorWorkerId'))
            evaluations = data.get('evaluations')

            # Update Gastronomy Evaluation
            monthlyEval.payTime = payTime
            monthlyEval.evaluateWorker = evaluateWorker
            monthlyEval.evaluateWorkerCharge = evaluateWorker.cargo
            monthlyEval.evaluatorWorker = evaluatorWorker
            monthlyEval.evaluatorWorkerCharge = evaluatorWorker.cargo
            monthlyEval.ind1_CDRI = evaluations[0].get('points')
            monthlyEval.ind2_AMD = evaluations[1].get('points')
            monthlyEval.ind3_PAPPI = evaluations[2].get('points')
            monthlyEval.ind4_CEDP = evaluations[3].get('points')
            monthlyEval.ind5_ROCR = evaluations[4].get('points')
            monthlyEval.ind6_PCRBBRC = evaluations[5].get('points')
            monthlyEval.ind7_CNPE = evaluations[6].get('points')
            monthlyEval.ind8_CCPC = evaluations[7].get('points')
            monthlyEval.ind9_NSC = evaluations[8].get('points')
            monthlyEval.ind10_CPI = evaluations[9].get('points')
            monthlyEval.ind11_INI = evaluations[10].get('points')
            monthlyEval.ind12_RAP = evaluations[11].get('points')
            monthlyEval.ind13_GV = evaluations[12].get('points')
            monthlyEval.ind14_DF = evaluations[13].get('points')
            monthlyEval.ind15_CTP = evaluations[14].get('points')
            monthlyEval.ind16_AC = evaluations[15].get('points')
            monthlyEval.ind17_DIS = evaluations[16].get('points')
            monthlyEval.ind18_CDPA = evaluations[17].get('points')
            monthlyEval.ind19_CTA = evaluations[18].get('points')
            monthlyEval.ind20_HOPT = evaluations[19].get('points')
            monthlyEval.ind21_CNSS = evaluations[20].get('points')
            monthlyEval.ind22_UIE = evaluations[21].get('points')
            monthlyEval.ind23_LCH = evaluations[22].get('points')
            monthlyEval.ind24_APAT = evaluations[23].get('points')
            monthlyEval.ind25_UCU = evaluations[24].get('points')
            monthlyEval.save()

            # Update Melia Evaluation
            monthlyMeliaEval = MonthlyMeliaEvaluation.objects.get(evaluateWorker=evaluateWorker, payTime=payTime)
            monthlyMeliaEval.payTime = payTime
            monthlyMeliaEval.evaluateWorker = evaluateWorker
            monthlyMeliaEval.evaluateWorkerCharge = evaluateWorker.cargo
            monthlyMeliaEval.evaluatorWorker = evaluatorWorker
            monthlyMeliaEval.evaluatorWorkerCharge = evaluatorWorker.cargo
            monthlyMeliaEval.asist_punt = getMaxEval(
                [monthlyEval.ind1_CDRI, monthlyEval.ind2_AMD, monthlyEval.ind24_APAT]
            )
            monthlyMeliaEval.dom_cum_tars = getMaxEval(
                [monthlyEval.ind10_CPI, monthlyEval.ind13_GV, monthlyEval.ind14_DF, monthlyEval.ind15_CTP,
                 monthlyEval.ind19_CTA]
            )
            monthlyMeliaEval.trab_equipo = getMaxEval(
                [monthlyEval.ind3_PAPPI, monthlyEval.ind17_DIS, monthlyEval.ind18_CDPA]
            )
            monthlyMeliaEval.cal_aten_cliente = getMaxEval(
                [monthlyEval.ind8_CCPC, monthlyEval.ind9_NSC, monthlyEval.ind16_AC, monthlyEval.ind20_HOPT,
                 monthlyEval.ind21_CNSS, monthlyEval.ind22_UIE, monthlyEval.ind23_LCH]
            )
            monthlyMeliaEval.cui_area_rec_medios = getMaxEval([monthlyEval.ind5_ROCR, monthlyEval.ind6_PCRBBRC])
            monthlyMeliaEval.cump_normas = getMaxEval(
                [monthlyEval.ind4_CEDP, monthlyEval.ind7_CNPE, monthlyEval.ind25_UCU]
            )
            monthlyMeliaEval.cap_camb_ini_int = getMaxEval([monthlyEval.ind11_INI, monthlyEval.ind12_RAP])
            monthlyMeliaEval.save()
            return Response({'Monthly Gastronomy Evaluation EDITED'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
