from rest_framework import routers
from apps.evaluation_in_area.viewsets.evaluation_area import EvaluationAreaViewSet
from apps.evaluation_in_area.viewsets.evaluation_aspect import EvaluationAspectViewSet
from apps.evaluation_in_area.viewsets.evaluation_summaries import get_ranges_of_month_melia_evaluations, \
    get_ranges_of_year_melia_evaluations, get_last_three_evaluation_periods
from apps.evaluation_in_area.viewsets.melia_aspect import MeliaAspectListView, MeliaAspectRetrieveView
from django.urls import path
from apps.evaluation_in_area.viewsets.month_evaluation import MonthEvaluationViewSet, \
    get_area_evaluation_given_worker_and_payment_period, get_evaluations_in_area_and_payment_period, \
    update_month_evaluation, get_month_evaluation_by_id, undo_month_area_evaluation, \
    update_melia_values_and_observations_month_evaluation, get_month_performance
from apps.evaluation_in_area.viewsets.year_evaluation import create_year_evaluation, list_year_evaluations, \
    get_year_evaluation_by_id, update_year_evaluation

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

    path('month-evaluation/melia/<int:month_evaluation_id>', update_melia_values_and_observations_month_evaluation),

    path('year-evaluation', create_year_evaluation),

    path('year-evaluation/all/<int:year>', list_year_evaluations),

    path('year-evaluation/<int:evaluation_id>', get_year_evaluation_by_id),

    path('year-evaluation/update/<int:evaluation_id>', update_year_evaluation),

    path('month-performance/<int:hotel_id>/<int:payment_period_id>', get_month_performance),

    path('summary/melia-month-evaluation-ranges', get_ranges_of_month_melia_evaluations),

    path('summary/melia-year-evaluation-ranges', get_ranges_of_year_melia_evaluations),

    path('summary/last-three-evaluation-periods', get_last_three_evaluation_periods)
]
