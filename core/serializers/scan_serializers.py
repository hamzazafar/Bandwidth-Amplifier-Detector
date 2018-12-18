from rest_framework import serializers

from core.models.scan import Scan

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_beat.validators import *

from .validators import *

from django.conf import settings

import pytz

CELERY_TIMEZONE = getattr(settings, "CELERY_TIMEZONE", "UTC")

class CronSerializer(serializers.ModelSerializer):

    minute = serializers.CharField(max_length=240, required=False)
    hour = serializers.CharField(max_length=96, required=False)
    day_of_week = serializers.CharField(max_length=64, required=False)
    day_of_month = serializers.CharField(max_length=124, required=False)
    month_of_year = serializers.CharField(max_length=64, required=False)
    timezone = serializers.CharField(read_only=True)

    class Meta:
        model = CrontabSchedule
        fields = '__all__'

    def validate_minute(self, value):
        return cron_validator(minute_validator, value)

    def validate_hour(self, value):
        return cron_validator(hour_validator, value)

    def validate_day_of_week(self, value):
        return cron_validator(day_of_week_validator, value)

    def validate_day_of_month(self, value):
        return cron_validator(day_of_month_validator, value)

    def validate_month_of_year(self, value):
        return cron_validator(month_of_year_validator, data['month_of_year'])


class ScanSerializer(serializers.ModelSerializer):

    crontab = CronSerializer()

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    def create(self, validated_data):
        cron_data = validated_data.pop("crontab")
        cron_minute = cron_data.get("minute", "*")
        cron_hour = cron_data.get("hour", "*")
        cron_day_of_week = cron_data.get("day_of_week", "*")
        cron_day_of_month = cron_data.get("day_of_month", "*")
        cron_month_of_year = cron_data.get("month_of_year", "*")

        crontab_obj,_ = CrontabSchedule.objects.get_or_create(minute=cron_minute,
                                                              hour=cron_hour,
                                                              day_of_week=cron_day_of_week,
                                                              day_of_month=cron_day_of_month,
                                                              month_of_year=cron_month_of_year,
                                                              timezone=CELERY_TIMEZONE)

        periodic_task_obj = PeriodicTask.objects.create(crontab=crontab_obj, **validated_data)
        return periodic_task_obj

"""
class ScanSerializer(serializers.ModelSerializer):
    address_range = serializers.CharField(allow_blank=False,
                                          max_length=255,
                                          validators=[address_range_validator],
                                          required=True)

    target_port = serializers.IntegerField(validators=[port_number_validator],
                                           required=True)

    class Meta:
        model = Scan
        fields = '__all__'
        read_only_fields = ('version',)
"""
