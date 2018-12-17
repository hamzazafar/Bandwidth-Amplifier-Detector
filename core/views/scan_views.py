from rest_framework import generics

from core.models.scan import Scan
from core.serializers.scan_serializers import ScanSerializer

from django_celery_beat.models import PeriodicTask

from rest_framework.response import Response

from core.tasks import add

class ScanListCreateView(generics.ListCreateAPIView):
    #queryset  = Scan.objects.all()
    queryset  = PeriodicTask.objects.all()
    serializer_class = ScanSerializer

    #def list(self, request):
    #    res = add.delay(5,1)
    #    print("%s" % res.ready())
    #    queryset = self.get_queryset()
    #    serializer = ScanSerializer(queryset, many=True)
    #    return Response(serializer.data)


class ScanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    #queryset  = Scan.objects.all()
    queryset = PeriodicTask.objects.all()
    serializer_class = ScanSerializer
