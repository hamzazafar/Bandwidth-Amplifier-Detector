from rest_framework import serializers

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_beat.validators import *

from .validators import *

from django.conf import settings

from ipaddress import ip_network

import json

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
        return cron_validator(month_of_year_validator, value)


class ScanArgsSerializer(serializers.Serializer):

    address_range = serializers.CharField(allow_blank=False,
                                          max_length=255,
                                          validators=[address_range_validator],
                                          required=True,
                                          write_only=True)

    target_port = serializers.IntegerField(validators=[port_number_validator],
                                           required=True,
                                           write_only=True)

class ScanSerializer(serializers.ModelSerializer):

    crontab = CronSerializer()
    scan_args = ScanArgsSerializer(write_only=True)

    scan_args_data = serializers.SerializerMethodField()

    class Meta:
        model = PeriodicTask
        fields = '__all__'
        read_only_fields = ('task', 'scan_args_data')

    def get_scan_args_data(self, obj):
        return json.loads(obj.kwargs)

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

        name = validated_data.pop("name")
        task = "core.tasks.scan"

        validated_scan_args = validated_data.pop('scan_args')
        kwargs = dict()

        kwargs["scan_name"] = name
        kwargs["address_range"] = validated_scan_args.pop('address_range').split(',')
        kwargs["target_port"] = validated_scan_args.pop('target_port')

        # set the IP address version
        kwargs["version"] = ip_network(kwargs["address_range"][0])._version

        periodic_task_obj = PeriodicTask.objects.create(crontab=crontab_obj,
                                                        name=name,
                                                        task=task,
                                                        kwargs=json.dumps(kwargs))
        return periodic_task_obj
