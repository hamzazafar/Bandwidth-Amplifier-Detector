"""
add models here
"""
from django.db import models

from django_celery_results.models import TaskResult

class ScanTimeSeriesResult(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    scan_name = models.CharField(null=False, max_length=255)
    active_amplifiers_count = models.IntegerField(null=False)
    status = models.CharField(null=False, max_length=255)

    # relations
    scan_result = models.OneToOneField(TaskResult,
                                       on_delete=models.CASCADE,
                                       related_name='time_series_result')

class Amplifier(models.Model):

    address = models.CharField(null=False, max_length=255)
    response_size = models.IntegerField(null=False)
    amplification_factor = models.IntegerField(null=False)

    # relations
    scan = models.ForeignKey(ScanTimeSeriesResult,
                             related_name='amplifiers',
                             on_delete=models.CASCADE)
