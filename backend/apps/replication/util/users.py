from apps.users.models import User


def delete_evaluator_users_with_deactivated_worker():
    users_to_delete = User.objects.filter(worker__activo=False)

    for user in users_to_delete:
        worker = user.worker
        worker.area_evaluacion = None
        worker.save()

        user.delete()
