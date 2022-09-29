from rest_framework import routers
from apps.evaluation_in_area.viewsets.evaluation_area import EvaluationAreaViewSet

router = routers.DefaultRouter()
router.register('evaluation-area', EvaluationAreaViewSet)
