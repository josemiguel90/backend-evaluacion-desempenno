from rest_framework.permissions import BasePermission

from apps.evaluation_in_area.models import EvaluationAspect
from apps.workers.models import Worker


class IsFoodAndDrinkBoss(BasePermission):
    """
    Allows access only to Food And Drink Boss users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.isFoodAndDrinkBoss)


class IsEvaluatorFromArea(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if user.is_anonymous or user.area is None:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'area'):
            return request.user.area == obj.area
        return True
