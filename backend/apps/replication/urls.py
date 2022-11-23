from django.urls import path
from apps.replication.views import replicate_data_from_zun, is_it_24_hours_since_replication

urlpatterns = [
    path('', replicate_data_from_zun),
    path('is-it-24-hours-since-replication', is_it_24_hours_since_replication)
]
