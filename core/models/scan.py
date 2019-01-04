"""
add models here
"""
from django.db import models

from django_celery_results.models import TaskResult

class ScanTimeSeriesResult(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    scan_name = models.CharField(null=False, max_length=255)
    scan_result = models.OneToOneField(TaskResult,
                                       on_delete=models.CASCADE,
                                       related_name='time_series_result')
    active_amplifiers_count = models.IntegerField(null=False)
