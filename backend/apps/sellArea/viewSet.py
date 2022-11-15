from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.extraPermissions import IsEvaluatorFromArea
from backend.utils import getSaleAreaDeleteError
from apps.hotel.models import Hotel

from .serializer import PuntoDeVenta, PuntoDeVentaSerializer


class PuntoDeVentaViewSet(viewsets.ModelViewSet):
    queryset = PuntoDeVenta.objects.all()
    serializer_class = PuntoDeVentaSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def getSellAreasByHotel(self, request):
        try:
            data = request.data
            hotel = Hotel.objects.get(pk=int(data.get('hotelId')))
            sellAreas = hotel.puntos_ventas.filter(activo=True)
            serializer = PuntoDeVentaSerializer(sellAreas, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteSelectedAreas(self, request):
        try:
            for area in request.data.get('items'):
                sellArea = PuntoDeVenta.objects.get(pk=area['id_pvta'])
                sellArea.activo = False
                sellArea.save()
            return Response({'Sell Areas Eliminated Successfully'}, status=status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({'detail': getSaleAreaDeleteError()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def rebuildSellAreaList(self, request):
        try:
            newSellAreas = request.data.get('newData')
            hotel = Hotel.objects.get(pk=int(request.data.get('hotelId')))
            for area in newSellAreas:
                myArea = PuntoDeVenta.objects.get(id_pvta=area['id_pvta'], hotel_id=hotel.id)
                if 'hasToRemove' in area:
                    myArea.activo = False
                    myArea.save()
                else:
                    myArea.cod_pvta = area['cod_pvta']
                    myArea.desc_pvta = area['desc_pvta']
                    myArea.activo = area['activo']
                    myArea.save()
            return Response({'Sell Areas Rebuilded Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def importSellAreas(self, request):
        try:
            data = request.data
            hotel = Hotel.objects.get(pk=int(data.get('hotelId')))
            for sellArea in data.get('sellAreas'):
                if PuntoDeVenta.objects.filter(id_pvta=sellArea.get('id_pvta'), hotel_id=hotel.pk).exists():
                    existingSellArea = PuntoDeVenta.objects.get(id_pvta=sellArea.get('id_pvta'))
                    existingSellArea.cod_pvta = sellArea.get('cod_pvta')
                    existingSellArea.desc_pvta = sellArea.get('desc_pvta')
                    existingSellArea.activo = sellArea.get('activo')
                    existingSellArea.save()
                else:
                    PuntoDeVenta.objects.create(
                        id_pvta=sellArea.get('id_pvta'),
                        cod_pvta=sellArea.get('cod_pvta'),
                        desc_pvta=sellArea.get('desc_pvta'),
                        activo=sellArea.get('activo'),
                        hotel=hotel
                    )
            return Response({'Sell Areas Updated Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
