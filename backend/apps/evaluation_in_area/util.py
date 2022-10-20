from typing import List

from rest_framework import status
from rest_framework.exceptions import ValidationError, ErrorDetail
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnDict


def handle_evaluation_area_validation_error(validation_error: ValidationError, request: Request) -> Response:
    error_dict: ReturnDict = validation_error.args[0]

    for field in error_dict:
        error_list = error_dict[field]
        error: ErrorDetail = error_list[0]
        message = f'{field}: {repr(error)}'

        if field == 'name' and error.code == 'unique':
            message = 'Ya existe un departamento con este nombre'
        elif field == 'name' and error.code == 'null':
            message = 'El nombre no puede ser nulo'
        elif field == 'name' and error.code == 'blank':
            message = 'El nombre no puede estar vacio'

        elif field == 'boss_charge' and error.code == 'null':
            message = 'El cargo del jefe no puede ser nulo'
        elif field == 'boss_charge' and error.code == 'does_not_exist':
            message = f'El cargo con id {request.data.get("boss_charge")} no existe'

        return Response({'detail': message}, status.HTTP_400_BAD_REQUEST)


def find_aspect_with_id_in_list(aspect_id: int , aspect_dict_list: List[dict]):
    for an_aspect in aspect_dict_list:
        if an_aspect['id'] == aspect_id:
            return an_aspect

    return Exception(f'Not found aspect with id {aspect_id}')
