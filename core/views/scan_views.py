from rest_framework import generics

from core.serializers.scan_serializers import ScanSerializer

from django_celery_beat.models import PeriodicTask


class ScanListCreateView(generics.ListCreateAPIView):
    queryset  = PeriodicTask.objects.all()
    serializer_class = ScanSerializer

class ScanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PeriodicTask.objects.all()
    serializer_class = ScanSerializer
