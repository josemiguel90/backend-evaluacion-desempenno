from django.urls import path
from apps.replication.views import replicate_data_from_zun


urlpatterns = [
    path('', replicate_data_from_zun)
]
