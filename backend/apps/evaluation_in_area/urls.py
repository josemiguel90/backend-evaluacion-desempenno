from rest_framework import routers
from apps.evaluation_in_area.viewsets.evaluation_area import EvaluationAreaViewSet
from apps.evaluation_in_area.viewsets.evaluation_aspect import EvaluationAspectViewSet
from apps.evaluation_in_area.viewsets.melia_aspect import MeliaAspectListView, MeliaAspectRetrieveView
from django.urls import path
from apps.evaluation_in_area.viewsets.month_evaluation import MonthEvaluationViewSet, \
    get_area_evaluation_given_worker_and_payment_period, get_evaluations_in_area_and_payment_period, \
    update_month_evaluation, get_month_evaluation_by_id, undo_month_area_evaluation, \
    update_melia_values_and_observations_month_evaluation

router = routers.DefaultRouter()
router.register('evaluation-area', EvaluationAreaViewSet)
router.register('evaluation-aspect', EvaluationAspectViewSet)
router.register('month-evaluation', MonthEvaluationViewSet)


urlpatterns = [
    path('melia-aspect', MeliaAspectListView.as_view()),
    path('melia-aspect/<int:pk>', MeliaAspectRetrieveView.as_view()),

    path('month-evaluation/area/<int:payment_period_id>/<str:worker_intern_number>',
         get_area_evaluation_given_worker_and_payment_period),

    path('month-evaluation/area/hotel/<int:hotel_id>/<int:payment_period_id>',
         get_evaluations_in_area_and_payment_period),

    path('month-evaluation/area/<int:month_evaluation_id>', update_month_evaluation),

    path('month-evaluation/area/get/<int:month_evaluation_id>', get_month_evaluation_by_id),

    path('month-evaluation/area/delete/<int:month_evaluation_id>', undo_month_area_evaluation),

    path('month-evaluation/melia/<int:month_evaluation_id>', update_melia_values_and_observations_month_evaluation)
]
