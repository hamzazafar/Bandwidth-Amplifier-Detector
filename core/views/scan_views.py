from rest_framework import generics

from core.models.scan import Scan
from core.serializers.scan_serializers import ScanSerializer

class ScanListCreateView(generics.ListCreateAPIView):
    queryset  = Scan.objects.all()
    serializer_class = ScanSerializer

class ScanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scan.objects.all()
    serializer_class = ScanSerializer
