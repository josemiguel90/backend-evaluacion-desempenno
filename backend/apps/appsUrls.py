from django.urls import path
from django.conf.urls import include
from rest_framework import routers
# Routers
from apps.users.urls import router as userRouter
from apps.hotel.urls import router as hotelRouter
from apps.family.urls import router as familyRouter
from apps.sellArea.urls import router as sellAreaRouter
from apps.workers.urls import router as workerRouter
from apps.currency.urls import router as currencyRouter
from apps.category.urls import router as categoryRouter
from apps.charge.urls import router as chargeRouters
from apps.salesPlan.urls import router as salesPlansRouters
from apps.payTime.urls import router as payTimeRouters
from apps.evaluation.urls import router as evaluationRouter
from .dashboardViews import views as dashViews
from apps.evaluation_in_area.urls import router as evaluation_in_area_router


class DefaulRouter(routers.DefaultRouter):
    def extend(self, extra_router):
        self.registry.extend(extra_router.registry)


router = DefaulRouter()
router.extend(userRouter)
router.extend(hotelRouter)
router.extend(familyRouter)
router.extend(sellAreaRouter)
router.extend(workerRouter)
router.extend(currencyRouter)
router.extend(categoryRouter)
router.extend(chargeRouters)
router.extend(salesPlansRouters)
router.extend(payTimeRouters)
router.extend(evaluationRouter)
router.extend(evaluation_in_area_router)

urlpatterns = [
    # Other Views, Login, User Profile, Update Password and others (Functional Views)
    path('', include('apps.users.urls')),
    path('', include('apps.hotel.urls')),
    path('', include('apps.evaluation.urls')),
    # DashBoard URLS and Views
    path('getMainNumbers/', dashViews.getMainNumbers),
    path('getRangeOfMelyaEvaluations/', dashViews.getRangeOfMelyaEvaluations),
    path('getRangeOfAnualEvaluations/', dashViews.getRangeOfAnualEvaluations),
    path('getTableEvaluations/', dashViews.getTableEvaluations),
    # Django Rest Framework Urls
    path('', include(router.urls)),
    # Evaluation Area Urls
    path('', include('apps.evaluation_in_area.urls'))
]
