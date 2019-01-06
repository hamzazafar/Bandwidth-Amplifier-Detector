from rest_framework import serializers

from core.models.scan import ScanTimeSeriesResult

from django_celery_results.models import TaskResult

import json

class TaskResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = TaskResult
        fields = '__all__'

class ScanResultSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='scan_result.status')
    amplifiers = serializers.SerializerMethodField()
    traceback = serializers.CharField(source='scan_result.traceback')

    def get_amplifiers(self, obj):
        result = json.loads(obj.scan_result.result)
        return result["amplifiers"]

    class Meta:
        model = ScanTimeSeriesResult
        fields = ('status',
                  'traceback',
                  'amplifiers',
                  'created',
                  'scan_name',
                  'active_amplifiers_count',)
