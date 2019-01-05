from django.urls import include, path
from .views.scan_views import ScanListCreateView, ScanRetrieveUpdateDestroyView

urlpatterns = [
    path('scan', ScanListCreateView.as_view()),
    path('scan/<str:name>', ScanRetrieveUpdateDestroyView.as_view()),
]
