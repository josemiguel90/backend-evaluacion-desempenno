from apps.category.models import OccupationalCategory
from apps.charge.models import Charge
from apps.workers.models import Worker


def get_worker_ids():
    queryset = Worker.objects.filter(activo=True).values_list('no_interno', flat=True)
    return [worker_id for worker_id in queryset]


def update_workers(updated_workers):

    for an_updated_worker in updated_workers:
        old_worker = Worker.objects.get(no_interno=an_updated_worker.get('no_interno'))
        old_worker.nombre = an_updated_worker.get('nombre')
        old_worker.apell1 = an_updated_worker.get('apell1')
        old_worker.apell2 = an_updated_worker.get('apell2')
        old_worker.cargo = Charge.objects.get(id_cargos=an_updated_worker['cargo']['id_cargos'])
        old_worker.cat_ocup = OccupationalCategory.objects.get(
            id_categ=an_updated_worker['cat_ocup']['id_categ'])
        old_worker.activo = an_updated_worker.get('activo')
        old_worker.save()
