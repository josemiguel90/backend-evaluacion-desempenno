from rest_framework.permissions import BasePermission


class IsFoodAndDrinkBoss(BasePermission):
    """
    Allows access only to Food And Drink Boss users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.isFoodAndDrinkBoss)


class IsEvaluatorFromArea(BasePermission):

    def has_permission(self, request, view):
        data = request.data
        if isinstance(data, list):
            return True

        area = data.get('area')

        user = request.user

        if user.is_anonymous or user.area is None:
            return False

        if area and user.area:
            return user.area.id == area
        return True

    def has_object_permission(self, request, view, obj):
        return request.user.area == obj.area
