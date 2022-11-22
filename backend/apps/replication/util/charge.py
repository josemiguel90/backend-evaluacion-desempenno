from apps.category.models import OccupationalCategory
from apps.charge.models import Charge


def replicate_charges(updated_charges):

    for a_updated_charge in updated_charges:

        try:
            found_charge = Charge.objects.get(id_cargos=a_updated_charge['id_cargos'])
            found_charge.cod_cargo = a_updated_charge['cod_cargo']
            found_charge.descripcion = a_updated_charge['descripcion']
            found_charge.fk_cat_ocupacion = OccupationalCategory.objects.get(
                id_categ=a_updated_charge['fk_cat_ocupacion'])
            found_charge.activo = a_updated_charge['activo']
            found_charge.save()

        except Charge.DoesNotExist:
            new_charge = Charge(id_cargos=a_updated_charge['id_cargos'],
                                cod_cargo=a_updated_charge['cod_cargo'],
                                descripcion=a_updated_charge['descripcion'],
                                fk_cat_ocupacion=OccupationalCategory.objects.get(
                                    id_categ=a_updated_charge['fk_cat_ocupacion']),
                                activo=a_updated_charge['activo'])
            new_charge.save()
