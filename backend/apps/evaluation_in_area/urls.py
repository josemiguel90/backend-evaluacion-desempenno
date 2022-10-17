from rest_framework import routers
from apps.evaluation_in_area.viewsets.evaluation_area import EvaluationAreaViewSet
from apps.evaluation_in_area.viewsets.melia_aspect import MeliaAspectEditionDeletionView, MeliaAspectCreationView, \
    MeliaAspectListView, MeliaAspectRetrieveView
from django.urls import path

router = routers.DefaultRouter()
router.register('evaluation-area', EvaluationAreaViewSet)


urlpatterns = [
    path('melia-aspect/<int:pk>/', MeliaAspectEditionDeletionView.as_view()),
    path('melia-aspect/', MeliaAspectCreationView.as_view()),
    path('melia-aspect', MeliaAspectListView.as_view()),
    path('melia-aspect/<int:pk>', MeliaAspectRetrieveView.as_view()),
]