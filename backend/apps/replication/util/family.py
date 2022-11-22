from apps.family.models import Family


def get_family_ids():
    queryset = Family.objects.filter(activo=True).values_list('id_grupo', flat=True)
    return [family_id for family_id in queryset]


def update_families(updated_families):

    for a_family in updated_families:
        family = Family.objects.get(id_grupo=a_family['id_grupo'])
        family.cod_grupo = a_family['cod_grupo']
        family.desc_grupo = a_family['desc_grupo']
        family.activo = a_family['activo']
        family.save()
