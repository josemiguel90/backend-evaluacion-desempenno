from rest_framework import serializers
from .models import Worker, Operador


class OperadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operador
        fields = '__all__'


class WorkerSerializer(serializers.ModelSerializer):
    cat_ocup = serializers.SerializerMethodField(read_only=True)
    cargo = serializers.SerializerMethodField(read_only=True)
    cargo_id = serializers.SerializerMethodField(read_only=True)
    hotel = serializers.SerializerMethodField(read_only=True)
    operador = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Worker
        fields = ['no_interno', 'nombreCompleto', 'cat_ocup',
                  'cargo', 'cargo_id', 'activo', 'hotel', 'operador', 'apell1', 'apell2']

    def get_cat_ocup(self, obj):
        return obj.cat_ocup.descripcion.title()

    def get_cargo(self, obj):
        return obj.cargo.descripcion.title()

    def get_cargo_id(self, obj):
        return obj.cargo.id_cargos

    def get_hotel(self, obj):
        return obj.unidad_org.id

    def get_operador(self, obj):
        if obj.operador is None:
            return False
        return OperadorSerializer(obj.operador, many=False).data
