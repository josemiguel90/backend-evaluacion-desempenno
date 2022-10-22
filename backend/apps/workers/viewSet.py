from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from backend.extraPermissions import IsEvaluatorFromArea
from backend.utils import getOperatorErrorMessage, getEvaluatorNotExistError
from .serializers import Worker, WorkerSerializer

from ..hotel.models import Hotel
from ..charge.models import OccupationalCategory, Charge
from .models import Operador
from backend.utils import getNeedCatForWorkerError, getNeedCharForWorkerError


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated, IsEvaluatorFromArea]

    @action(detail=False, methods=['POST'])
    def getWorkersByHotel(self, request):
        try:
            if OccupationalCategory.objects.all().count() == 0:
                raise Exception(getNeedCatForWorkerError())
            elif Charge.objects.all().count() == 0:
                raise Exception(getNeedCharForWorkerError())
            else:
                hotel = Hotel.objects.get(pk=int(request.data))
                hotels = hotel.workers.filter(activo=True, area_evaluacion=request.user.area).order_by('nombre')
                serializer = WorkerSerializer(hotels, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteOperator(self, request):
        data = request.data
        try:
            worker = Worker.objects.get(no_interno=data.get('workerId'))
            operator = Operador.objects.get(id_oper=data.get('operatorId'))
            worker.operador = None
            worker.save()
            operator.delete()
            return Response({'Operator Deleted Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def setOperator(self, request):
        data = request.data
        try:
            worker = Worker.objects.get(no_interno=data.get('workerId'))
            operator = data.get('operator')
            if not Operador.objects.filter(id_oper=operator['id_oper']).exists():
                newOp = Operador.objects.create(
                    id_oper=operator['id_oper'],
                    nombre=operator['nombre'],
                    descripcion=operator['descripcion']
                )
                worker.operador = newOp
            else:
                myOp = Operador.objects.get(id_oper=operator['id_oper'])
                myOp.nombre = operator['nombre']
                myOp.descripcion = operator['descripcion']
                myOp.save()
                worker.operador = myOp
            worker.save()
            return Response({'Operator Setted Successfully'}, status=status.HTTP_200_OK)
        except IntegrityError:
            message = getOperatorErrorMessage(int(data['operator']['id_oper']))
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def deleteWorkers(self, request):
        try:
            for worker in request.data:
                w = Worker.objects.get(no_interno=worker['no_interno'])
                masDelete = False
                op = None
                if w.operador is not None:
                    masDelete = True
                    op = w.operador
                w.activo = False
                w.area_evaluacion = None
                w.save()
                if masDelete:
                    op.delete()
            return Response({'Workers Deleted Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def rebuildList(self, request):
        try:
            newWorkers = request.data.get('newData')
            hotel = Hotel.objects.get(pk=int(request.data.get('hotelId')))
            for worker in newWorkers:
                myWorker = hotel.workers.get(no_interno=worker['no_interno'])
                if 'hasToRemove' in worker:
                    myWorker.activo = False
                    myWorker.save()
                else:
                    myWorker.nombre = worker['nombre']
                    myWorker.apell1 = worker['apell1']
                    myWorker.apell2 = worker['apell2']
                    myWorker.cat_ocup = OccupationalCategory.objects.get(id_categ=worker['cat_ocup']['id_categ'])
                    myWorker.cargo = Charge.objects.get(id_cargos=worker['cargo']['id_cargos'])
                    myWorker.activo = True
                    myWorker.save()
            return Response({'Worker List Rebuilded Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def importWorkers(self, request):
        try:
            hotelId = int(request.data['hotelId'])
            workers = request.data['items']
            hotel = Hotel.objects.get(pk=hotelId)

            for worker in workers:
                if Worker.objects.filter(no_interno=worker['no_interno']).exists():
                    w = Worker.objects.get(no_interno=worker['no_interno'])
                    w.nombre = worker['nombre']
                    w.apell1 = worker['apell1']
                    w.apell2 = worker['apell2']
                    w.cat_ocup = OccupationalCategory.objects.get(id_categ=worker['cat_ocup']['id_categ'])
                    w.cargo = Charge.objects.get(id_cargos=worker['cargo']['id_cargos'])
                    w.activo = True
                    w.unidad_org = hotel
                    w.area_evaluacion = request.user.area
                    w.save()
                else:
                    Worker.objects.create(
                        no_interno=worker['no_interno'],
                        nombre=worker['nombre'],
                        apell1=worker['apell1'],
                        apell2=worker['apell2'],
                        cat_ocup=OccupationalCategory.objects.get(id_categ=worker['cat_ocup']['id_categ']),
                        cargo=Charge.objects.get(id_cargos=worker['cargo']['id_cargos']),
                        activo=True,
                        area_evaluacion=request.user.area,
                        unidad_org=hotel
                    )
            return Response({'Workers Imported Successfully'}, status=status.HTTP_200_OK)
        except OccupationalCategory.DoesNotExist:
            message = getNeedCatForWorkerError()
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Charge.DoesNotExist:
            message = getNeedCharForWorkerError()
            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def getEvaluatorDetails(self, request):
        try:
            worker = Worker.objects.get(cargo__id_cargos=14)
            serializer = WorkerSerializer(worker, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Worker.DoesNotExist:
            try:
                worker = Worker.objects.get(cargo__id_cargos=63)
                serializer = WorkerSerializer(worker, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Worker.DoesNotExist:
                return Response({'detail': getEvaluatorNotExistError()}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
