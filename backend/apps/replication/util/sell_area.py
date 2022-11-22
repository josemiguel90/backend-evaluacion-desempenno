from apps.hotel.models import Hotel
from apps.sellArea.models import PuntoDeVenta


def get_sell_area_ids():
    sell_areas_queryset = PuntoDeVenta.objects.filter(activo=True)\
        .values_list('id_pvta', flat=True)
    return [an_id for an_id in sell_areas_queryset]


def update_sell_areas(sell_areas):

    for a_sell_area in sell_areas:
        area = PuntoDeVenta.objects.get(id_pvta=a_sell_area.get('id_pvta'))
        area.cod_pvta = a_sell_area.get('cod_pvta')
        area.desc_pvta = a_sell_area.get('desc_pvta')
        area.activo = a_sell_area.get('activo')
        area.save()


def get_pos_db_names():
    return [hotel.pos_db_name for hotel in Hotel.objects.all()]
