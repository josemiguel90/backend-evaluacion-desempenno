from django.contrib.auth.hashers import make_password
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from backend import utils
from ..models import User
from ..serializers.userSerializer import UserSerializer, UserMiniSerializer, UserSerializerWithToken
from ..util import check_user_unique_fields
from ...category.models import OccupationalCategory
from ...charge.models import Charge
from ...evaluation_in_area.models import EvaluationArea
from ...hotel.models import Hotel
from ...workers.models import Worker


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by('pk')
    serializer_class = UserMiniSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(self.get_object(), many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def deleteUsers(self, request):
        try:
            for user in request.data:
                user_instance = get_user_model().objects.get(pk=user.get('id'))
                worker = user_instance.worker

                user_instance.delete()
                if worker:
                    worker.activo = False
                    worker.area_evaluacion = None
                    worker.save()

            return Response({'Users Eliminated Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'])
    def changePassword(self, request, pk=None):
        try:
            user = get_user_model().objects.get(pk=pk)
            user.password = make_password(request.data.get('password'))
            user.save()
            return Response({'Password Changed Successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data
        evaluation_area = None
        worker = None

        bad_request_response = check_user_unique_fields(data)
        if bad_request_response:
            return bad_request_response

        if data.get('isAdmin') and data.get('area'):
            return Response({'detail': 'Un usuario no puede ser evaluador y administrador del sistema al mismo tiempo'},
                            status.HTTP_400_BAD_REQUEST)

        try:
            if data.get('area'):
                evaluation_area = EvaluationArea.objects.get(pk=data.get('area'))

            if not data.get('isAdmin'):
                worker = self.get_worker_instance(data.get('worker'), evaluation_area)
                worker.save()

            first_name = worker.nombre if worker else data.get('first_name')
            last_name = f'{worker.apell1} {worker.apell2}' if worker else data.get('last_name')

            User(
                username=data.get('username'),
                first_name=first_name,
                last_name=last_name,
                email=data.get('email'),
                is_staff=data.get('isAdmin'),
                password=make_password(data.get('password')),
                worker=worker,
                area=evaluation_area
            ).save()

            return Response({'Users Created Successfully'}, status=status.HTTP_200_OK)

        except EvaluationArea.DoesNotExist:
            return Response({'detail': f'El área con id {data.get("area")} no existe'}, status.HTTP_404_NOT_FOUND)

        except Worker.DoesNotExist:
            return Response({'detail': f'El trabajador con id {data.get("workerId")} no existe'},
                            status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            message = e.args[0]
            if 'area_id' in e.args[0]:
                message = f'El área {evaluation_area.name} ya fue asignada'

            return Response({'detail': message}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def get_worker_instance(self, worker_from_request, evaluation_area):
        found_worker = Worker.objects.filter(
            no_interno=worker_from_request['no_interno']).first()

        occupational_category = OccupationalCategory.objects.get(
            id_categ=worker_from_request['cat_ocup']['id_categ'])

        hotel = Hotel.objects.get(zunPrUnidadOrganizativaId=worker_from_request['unidad_org'])

        charge = Charge.objects.get(pk=worker_from_request['cargo']['id_cargos'])

        if found_worker:
            found_worker.nombre = worker_from_request['nombre']
            found_worker.apell1 = worker_from_request['apell1']
            found_worker.apell2 = worker_from_request['apell2']
            found_worker.unidad_org = hotel
            found_worker.cat_ocup = occupational_category
            found_worker.cargo = Charge.objects.get(id_cargos=worker_from_request['cargo']['id_cargos'])
            found_worker.activo = worker_from_request['activo']
            found_worker.area_evaluacion = evaluation_area
            return found_worker

        return Worker(no_interno=worker_from_request['no_interno'],
                      nombre=worker_from_request['nombre'],
                      apell1=worker_from_request['apell1'],
                      apell2=worker_from_request['apell2'],
                      unidad_org=hotel,
                      cat_ocup=occupational_category,
                      cargo=charge,
                      activo=worker_from_request['activo'],
                      area_evaluacion=evaluation_area)

    def update(self, request, *args, **kwargs):
        data = request.data
        evaluation_area_id = data.get('area')
        new_worker = None
        user = self.get_object()

        if data.get('isAdmin') and data.get('area') and data.get('worker'):
            return Response({'detail': 'Un usuario no puede ser evaluador y administrador del sistema al mismo tiempo'},
                            status.HTTP_400_BAD_REQUEST)

        bad_request_response = check_user_unique_fields(data, user.id)
        if bad_request_response:
            return bad_request_response

        try:
            """ Validate only an Admin user """
            onlyOneAdmin = get_user_model().objects.filter(is_staff=True).count() == 1
            if user.is_staff and not data.get('isAdmin') and onlyOneAdmin:
                raise Exception(utils.getNoAdminDeleteMessage(user.username))

            # get evaluation area
            evaluation_area = EvaluationArea.objects.get(pk=evaluation_area_id) if evaluation_area_id else None

            # Desvincular al trabajador del área con la que estaba asociado
            if user.worker:
                old_worker = user.worker
                old_worker.area_evaluacion = None
                old_worker.save()

            if data.get('worker'):
                new_worker = self.get_worker_instance(data.get('worker'), evaluation_area)
                new_worker.save()

            first_name = new_worker.nombre.title() if new_worker else data.get('first_name')

            last_name = f'{new_worker.apell1} {new_worker.apell2}' if new_worker else data.get('last_name')

            """ Edit User Fields """
            user.username = data.get('username')
            user.first_name = first_name
            user.last_name = last_name
            user.email = data.get('email')
            user.is_staff = data.get('isAdmin')
            user.area = evaluation_area
            user.worker = new_worker

            user.save()

            """ Return Response """
            return Response({'Users Edited Successfully'}, status=status.HTTP_200_OK)

        except EvaluationArea.DoesNotExist:
            return Response({'detail': f'El área de evaluación con id {evaluation_area_id} no existe'},
                            status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


""" Authenticated User Views, thats the reason for the functional Views and is not inside the Class ViewSet"""


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAuthenticatedUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False).data
    return Response(serializer)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    data = request.data

    bad_request_response = check_user_unique_fields(data, user.id)
    if bad_request_response:
        return bad_request_response

    try:
        user.username = data.get('username')
        user.first_name = data.get('first_name')
        user.last_name = data.get('last_name')
        user.email = data.get('email')
        user.save()
        return Response(UserSerializerWithToken(user, many=False).data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserPassword(request):
    user = request.user
    data = request.data
    try:
        if not user.check_password(data.get('oldPassword')):
            raise Exception('La actual contraseña no es correcta, inténtelo de nuevo')
        user.password = make_password(data.get('newPassword'))
        user.save()
        return Response(UserSerializerWithToken(user, many=False).data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
