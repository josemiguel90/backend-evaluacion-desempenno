from apps.currency.models import Currency


def replicate_currencies(updated_currencies):

    for an_updated_currency in updated_currencies:
        try:
            found_currency = Currency.objects.get(id=an_updated_currency['id'])
            found_currency.acronym = an_updated_currency['acronym']
            found_currency.description = an_updated_currency['description']
            found_currency.save()

        except Currency.DoesNotExist:
            new_currency = Currency(id=an_updated_currency['id'],
                                    acronym=an_updated_currency['acronym'],
                                    description=an_updated_currency['description'],
                                    active=True)
            new_currency.save()

    updated_currency_ids = list(map(lambda currency: currency['id'], updated_currencies))

    # Marcar como eliminado las monedas que no se devuelven por el ZUN
    for a_currency in Currency.objects.all():
        if a_currency.id not in updated_currency_ids:
            a_currency.active = False
            a_currency.save()
