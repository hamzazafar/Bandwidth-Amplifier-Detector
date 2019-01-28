from rest_framework import serializers

from core.models.scan import ScanTimeSeriesResult

import json

class ScanResultSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='scan_result.status')
    amplifiers = serializers.SerializerMethodField()
    traceback = serializers.CharField(source='scan_result.traceback')

    def get_amplifiers(self, obj):
        if obj.status == "SUCCESS":
            result = json.loads(obj.scan_result.result)
            return result["amplifiers"]
        return None

    class Meta:
        model = ScanTimeSeriesResult
        fields = ('status',
                  'traceback',
                  'amplifiers',
                  'created',
                  'scan_name',
                  'active_amplifiers_count',)
