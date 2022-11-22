from apps.category.models import OccupationalCategory


def replicate_categories(updated_categories):

    for an_updated_category in updated_categories:

        try:
            found_category = OccupationalCategory.objects.get(
                id_categ=an_updated_category['id_categ'])
            found_category.cod_categ = an_updated_category['cod_categ']
            found_category.descripcion = an_updated_category['descripcion']
            found_category.activo = an_updated_category['activo']
            found_category.save()

        except OccupationalCategory.DoesNotExist:
            new_category = OccupationalCategory(id_categ=an_updated_category['id_categ'],
                                                cod_categ=an_updated_category['cod_categ'],
                                                descripcion=an_updated_category['descripcion'],
                                                activo=an_updated_category['activo'])
            new_category.save()
