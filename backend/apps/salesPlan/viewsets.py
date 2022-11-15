from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from backend.extraPermissions import IsEvaluatorFromArea
from backend.utils import getAnualPlanError, getAnualPlanDeleteError, getMonthlySalePlanCreateError
from .serializers import AnualSalePlanSerializer, AnualSalePlan, AnualSalePlanMiniSerializer, MonthlySalePlan, \
    MonthlySalePlanForEditSerializer
from ..hotel.models import Hotel
from ..currency.models import Currency
from ..family.models import Family
from ..sellArea.models import PuntoDeVenta


class AnualSalePlanViewSet(viewsets.ModelViewSet):
    queryset = AnualSalePlan.objects.all().order_by('-year')
    serializer_class = AnualSalePlanMiniSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    def retrieve(self, request, *args, **kwargs):
        serializer = AnualSalePlanSerializer(self.get_object(), many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        try:
            year = data.get('year')
            hotel = Hotel.objects.get(id=data['hotel']['id'])
            coin = Currency.objects.get(id=data['coin']['id'])
            AnualSalePlan.objects.create(
                hotel=hotel,
                currency=coin,
                year=year
            )
            return Response({'Anual Sale Plan Added'}, status=status.HTTP_200_OK)
        except IntegrityError:
            message = getAnualPlanError(
                data['year'], data['hotel']['name'], data['coin']['name'])
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def getHotelAnualSalePlans(self, request):
        try:
            hotel = Hotel.objects.get(pk=int(request.data.get('hotelId')))
            anualPlans = hotel.anualSalePlans.all().order_by('-year')
            serializer = AnualSalePlanMiniSerializer(anualPlans, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def getMiniDetails(self, request, pk=None):
        try:
            anualPlan = AnualSalePlan.objects.get(pk=pk)
            serializer = AnualSalePlanMiniSerializer(anualPlan, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def editAnualSalePlan(self, request, pk=None):
        data = request.data
        try:
            anualSalePlan = AnualSalePlan.objects.get(pk=pk)
            anualSalePlan.year = data.get('year')
            anualSalePlan.save()
            return Response({"Anual Sale Plan Edited"}, status=status.HTTP_200_OK)
        except IntegrityError:
            message = getAnualPlanError(
                data['year'], data['hotel'], data['coin'])
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteAnualPlans(self, request):
        data = request.data
        try:
            for asl in data:
                myAsl = AnualSalePlan.objects.get(pk=int(asl.get('id')))
                myAsl.delete()
            return Response({"Anual Sale Plans Deleted"}, status=status.HTTP_200_OK)
        except IntegrityError:
            message = getAnualPlanDeleteError()
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteMonthlySalePlans(self, request):
        data = request.data
        try:
            for msp in data:
                myMsp = MonthlySalePlan.objects.get(pk=int(msp.get('id')))
                myMsp.delete()
            return Response({"Monthly Sale Plans Deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def createMonthlySalePlan(self, request):
        data = request.data
        try:
            anualSalePlan = AnualSalePlan.objects.get(pk=int(data.get('anualSalePlanId')))
            month = data.get('month')
            family = Family.objects.get(id_grupo=int(data.get('familyId')))
            saleArea = PuntoDeVenta.objects.get(id_pvta=int(data.get('saleAreaId')))
            plan = data.get('plan')
            MonthlySalePlan.objects.create(
                anualSalePlan=anualSalePlan,
                month=month,
                family=family,
                saleArea=saleArea,
                plan=plan
            )
            return Response({"Monthly Sale Plans Created"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            message = getMonthlySalePlanCreateError()
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def editMonthlySalePlan(self, request):
        data = request.data
        try:
            anualSalePlan = AnualSalePlan.objects.get(pk=int(data.get('anualSalePlanId')))
            monthlySalePlan = anualSalePlan.monthlySalePlans.get(pk=int(data.get('monthlySalePlanId')))
            monthlySalePlan.month = data.get('month')
            monthlySalePlan.family = Family.objects.get(id_grupo=int(data.get('familyId')))
            monthlySalePlan.saleArea = PuntoDeVenta.objects.get(id_pvta=data.get('saleAreaId'))
            monthlySalePlan.plan = data.get('plan')
            monthlySalePlan.save()
            return Response({"Monthly Sale Plans Edited"}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            message = getMonthlySalePlanCreateError()
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def getMonthlySalePlanDetails(self, request, pk=None):
        monthlySalePlanId = request.data
        try:
            anualSalePlan = AnualSalePlan.objects.get(pk=pk)
            monthlySalePlan = anualSalePlan.monthlySalePlans.get(pk=monthlySalePlanId)
            serializer = MonthlySalePlanForEditSerializer(monthlySalePlan, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def getYearSalesReport(self, request):
        try:
            anualSalePlan = AnualSalePlan.objects.get(pk=int(request.data))
            return Response(anualSalePlan.getReport(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
