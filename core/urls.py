from django.urls import include, path

from .views.scan_views import ScanListCreateView, ScanRetrieveUpdateDestroyView, get_scan_results

urlpatterns = [
    path('scan', ScanListCreateView.as_view()),
    path('scan/<str:name>', ScanRetrieveUpdateDestroyView.as_view()),
    path('scan/<str:name>/result', get_scan_results)
]
