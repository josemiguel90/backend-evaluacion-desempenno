from rest_framework import status
from rest_framework.response import Response
from apps.users.models import User


def check_user_unique_fields(data, user_id=None):
    username = data.get('username')

    other_users = User.objects.exclude(id=user_id)

    if other_users.filter(username=data.get('username')).count() > 0:
        return Response({'detail': f'Ya existe un usuario con Nombre de Usuario \'{username}\''},
                        status.HTTP_400_BAD_REQUEST)

    email = data.get('email')
    if other_users.filter(email=data.get('email')).count() > 0:
        return Response({'detail': f'Ya existe un usuario con el email \'{email}\''},
                        status.HTTP_400_BAD_REQUEST)