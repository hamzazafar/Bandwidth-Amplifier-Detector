"""
add models here
"""
from django.db import models

from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask

class ScanTimeSeriesResult(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    scan_name = models.CharField(null=False, max_length=255)
    active_amplifiers_count = models.IntegerField(null=False)
    status = models.CharField(null=False, max_length=255)

    # relations
    scan_result = models.OneToOneField(TaskResult,
                                       on_delete=models.CASCADE,
                                       related_name='time_series_result')

    periodic_task = models.ForeignKey(PeriodicTask,
                                      on_delete=models.CASCADE,
                                      related_name='time_series_results')

class Amplifier(models.Model):

    address = models.CharField(null=False, max_length=255)
    total_response_size = models.IntegerField(null=False)
    amplification_factor = models.IntegerField(null=False)
    unsolicited_response = models.BooleanField(default=False)

    # relations
    scan = models.ForeignKey(ScanTimeSeriesResult,
                             related_name='amplifiers',
                             on_delete=models.CASCADE)

class Response(models.Model):

    response_hex_data = models.TextField(null=False)
    response_size = models.IntegerField(null=False)

    #relations
    amplifier = models.ForeignKey(Amplifier,
                                  related_name="responses",
                                  on_delete=models.CASCADE)

