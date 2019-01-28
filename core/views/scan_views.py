from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from core.serializers.scan_serializers import ScanSerializer
from core.serializers.scan_result_serializers import ScanResultSerializer

from core.tasks import scan

from core.models.scan import ScanTimeSeriesResult

from django_celery_beat.models import PeriodicTask

from django_celery_results.models import TaskResult

from celery.task.control import revoke
from celery.task.control import inspect

from django.shortcuts import get_list_or_404, get_object_or_404

import json

class ScanListCreateView(generics.ListCreateAPIView):
    queryset  = PeriodicTask.objects.all()
    serializer_class = ScanSerializer

class ScanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PeriodicTask.objects.all()
    serializer_class = ScanSerializer
    lookup_field = 'name'

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


@api_view(['GET'])
def get_running_scans(request):
    try:
        i = inspect()
        data = i.active()

        if not data:
            return Response(status=status.HTTP_404_NOT_FOUND)

        running_scans = list()
        for k,val in data.items():
            for v in val:
                running_scans.append(v)

        return Response(status=status.HTTP_404_NOT_FOUND,
                        data=running_scans)

    except Exception as err:
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={"Details": str(err)})

@api_view(['GET'])
def revoke_scan(request, task_id):
    try:
        revoke(task_id,
               terminate=True,
               signal='SIGKILL')
    except Exception as err:
        return Response(status=status.HTTP_404_NOT_FOUND,
                        data={"Details": str(err)})

    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_scan_results(request, name):
    # by default return only the most recent result
    latest = int(request.query_params.get('latest', 1))

    if latest == 1:
        # return the most recent result if query params is not specified
        try:
            result = ScanTimeSeriesResult.objects.filter(scan_name=name).latest('created')
            serializer = ScanResultSerializer(result)
        except ScanTimeSeriesResult.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={"Details": "Not Found"})
    else:
        result = get_list_or_404(ScanTimeSeriesResult.objects.order_by('created'),
                                 scan_name=name)

        if latest > 1:
            latest = latest * -1
            serializer = ScanResultSerializer(result[latest:], many=True)
        else:
            serializer = ScanResultSerializer(result, many=True)

    return Response(serializer.data)
