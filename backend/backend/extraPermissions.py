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
        area = data.get('area')
        return request.user.area.id == area

    def has_object_permission(self, request, view, obj):
        return request.user.area == obj.area
