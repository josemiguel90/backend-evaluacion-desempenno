from django.http import HttpResponseServerError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import io

from apps.replication.models import Replication
from apps.replication.util.category import replicate_categories
from apps.replication.util.charge import replicate_charges
from apps.replication.util.currency import replicate_currencies
from apps.replication.util.family import get_family_ids, update_families
from apps.replication.util.payment_period import replicate_payment_period
from apps.replication.util.sell_area import get_sell_area_ids, update_sell_areas, get_pos_db_names
from apps.replication.util.users import delete_evaluator_users_with_deactivated_worker
from apps.replication.util.worker import get_worker_ids, update_workers
import requests
from apps.replication.util.zun_url import get_zun_url
from datetime import timedelta
from django.utils import timezone


def send_replication_request() -> requests.Response:
    sell_area_ids = get_sell_area_ids()
    pos_db_names = get_pos_db_names()
    workers_ids = get_worker_ids()
    family_ids = get_family_ids()

    data = {'sellAreaIds': sell_area_ids,
            'posDBNames': pos_db_names,
            'workerIds': workers_ids, 'familyIds': family_ids}

    try:
        return requests.post(url=get_zun_url(), json=data,
                             headers={'Content-Type': 'application/json'})
    except Exception:
        return None


def is_it_24_hours_ago_since_last_replication():
    replications = Replication.objects.all()

    if replications.count() == 0:
        return True

    last_replication = replications.first()
    time_difference = timezone.now() - last_replication.time_stamp

    return time_difference >= timedelta(hours=24)


def set_last_replication(request):
    replications = Replication.objects.all()

    if replications.count() == 0:
        Replication(username=request.user.username).save()
    else:
        replication = replications.first()
        replication.time_stamp = timezone.now()
        replication.username = request.user.username
        replication.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def replicate_data_from_zun(request):

    force_replication = request.data.get('force')

    if not force_replication and (not is_it_24_hours_ago_since_last_replication()):
        return Response(status=status.HTTP_200_OK)

    response = send_replication_request()
    if response is None:
        return Response('No se pudo conectar con el Zun', status.HTTP_503_SERVICE_UNAVAILABLE)

    if response.status_code != requests.codes.ok:
        return Response('No se pudo conectar con el ZUN',
                        status.HTTP_503_SERVICE_UNAVAILABLE)

    response_as_bytes = bytes(response.text, encoding='utf8')
    response_stream = io.BytesIO(response_as_bytes)
    data = JSONParser().parse(response_stream)

    replicate_categories(data['categories'])
    replicate_charges(data['charges'])
    replicate_payment_period(data['payment_periods'])
    replicate_currencies(data['currencies'])

    # Estos objetos son seleccionables por el usuario
    # Por lo tanto sólo se actualizan los objetos activos
    update_workers(data['workers'])
    update_sell_areas(data['sell_areas'])
    update_families(data['families'])

    delete_evaluator_users_with_deactivated_worker()

    set_last_replication(request)

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_it_24_hours_since_replication(request):

    return Response({'isIt24HoursAgo': is_it_24_hours_ago_since_last_replication()},
                    status.HTTP_200_OK)

