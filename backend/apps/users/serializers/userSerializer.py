from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers

from apps.evaluation_in_area.serializers.evaluation_area import EvaluationAreaSerializer
from apps.users.models import User
from apps.workers.serializers import WorkerSerializer


class UserMiniSerializer(serializers.ModelSerializer):
    isAdmin = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    rol = serializers.SerializerMethodField(read_only=True)
    area = EvaluationAreaSerializer(read_only=True)
    worker = WorkerSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'rol', 'isAdmin', 'area', 'worker']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        if obj.worker:
            return obj.worker.nombreCompleto()

        # Eset es el nombre de un usuario administrador
        return obj.get_full_name()

    def get_email(self, obj):
        return obj.email if obj.email != '' else 'No registrado'

    def get_rol(self, obj):
        print(obj.area)
        if self.get_isAdmin(obj):
            return 'Administrador del sistema'

        if obj.area:
            return obj.area.boss_charge.descripcion

        return 'Usuario normal'

    def get_worker(self, obj):
        if obj.worker:
            return WorkerSerializer(obj.worker).data
        return None

class UserSerializer(UserMiniSerializer):
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol',
                  'isAdmin', 'date_joined', 'last_login', 'permissions', 'area',
                  'worker']

    def get_permissions(self, obj):
        permissions = obj.get_user_permissions()
        return permissions


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    area = EvaluationAreaSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'name', 'isAdmin', 'rol', 'token', 'area', 'worker']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
