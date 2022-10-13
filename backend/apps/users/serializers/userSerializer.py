from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers


class UserMiniSerializer(serializers.ModelSerializer):
    isAdmin = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)
    isFoodAndDrinkBoss = serializers.SerializerMethodField(read_only=True)
    rol = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'name', 'email', 'rol', 'isAdmin', 'isFoodAndDrinkBoss', 'area']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_name(self, obj):
        return obj.get_full_name()

    def get_email(self, obj):
        return obj.email if obj.email != '' else 'No registrado'

    def get_isFoodAndDrinkBoss(self, obj):
        return obj.isFoodAndDrinkBoss

    def get_rol(self, obj):
        print(obj.area)
        if self.get_isAdmin(obj):
            return 'Administrador'
        if self.get_isFoodAndDrinkBoss(obj):
            return 'Jefe de Alimentos y Bebidas del complejo'

        if obj.area:
            return obj.area.boss_charge.descripcion

        return 'Usuario normal'


class UserSerializer(UserMiniSerializer):
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'isAdmin', 'isFoodAndDrinkBoss',
                  'date_joined', 'last_login', 'permissions', 'area']

    def get_permissions(self, obj):
        permissions = obj.get_user_permissions()
        return permissions


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'name', 'isAdmin', 'isFoodAndDrinkBoss', 'rol', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)
