from django.urls import include, path

from .views.scan_views import (ScanListCreateView,
                               ScanRetrieveUpdateDestroyView,
                               get_scan_results,
                               get_running_scans,
                               revoke_scan)

urlpatterns = [
    path('scan', ScanListCreateView.as_view()),
    path('scan/running', get_running_scans),
    path('scan/<str:name>', ScanRetrieveUpdateDestroyView.as_view()),
    path('scan/<str:name>/result', get_scan_results),
    path('scan/revoke/<str:task_id>', revoke_scan)
]
