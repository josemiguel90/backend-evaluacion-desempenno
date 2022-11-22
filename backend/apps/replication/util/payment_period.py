from apps.payTime.models import PayTime
from backend.utils import getDateByStrig


def replicate_payment_period(updated_payment_periods):

    for an_updated_period in updated_payment_periods:
        try:
            found_period = PayTime.objects.get(id=an_updated_period['id_peri'])
            found_period.month = an_updated_period['nombre']
            found_period.monthOrder = an_updated_period['orden']
            found_period.initialDate = getDateByStrig(an_updated_period['fecha_inicio'])
            found_period.endDate = getDateByStrig(an_updated_period['fecha_fin'])
            found_period.year = an_updated_period['ejercicio']
            found_period.save()

        except PayTime.DoesNotExist:
            new_period = PayTime(id=an_updated_period['id_peri'],
                                 month=an_updated_period['nombre'],
                                 monthOrder=an_updated_period['orden'],
                                 initialDate=getDateByStrig(an_updated_period['fecha_inicio']),
                                 endDate=getDateByStrig(an_updated_period['fecha_fin']),
                                 year=an_updated_period['ejercicio'])
            new_period.save()
