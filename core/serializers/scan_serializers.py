from rest_framework import serializers

from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django_celery_beat.validators import *

from .validators import *

from django.conf import settings

from ipaddress import ip_network

import json

CELERY_TIMEZONE = getattr(settings, "CELERY_TIMEZONE", "UTC")
ZMAP_PACKETS_PER_SECOND = getattr(settings, "ZMAP_PACKETS_PER_SECOND")
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
                                          validators=[address_range_validator],
                                          required=True,
                                          write_only=True)

    target_port = serializers.IntegerField(validators=[port_number_validator],
                                           required=True,
                                           write_only=True)

    request_hexdump = serializers.CharField(allow_blank=False,
                                           write_only=True,
                                           required=True)

    packets_per_second = serializers.IntegerField(default=ZMAP_PACKETS_PER_SECOND,
                                                  write_only=True,
                                                  required=False)

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

    def update(self, instance, validated_data):
        cron_data = validated_data.pop("crontab")
        cron_minute = cron_data.get("minute", instance.crontab.minute)
        cron_hour = cron_data.get("hour", instance.crontab.hour)
        cron_day_of_week = cron_data.get("day_of_week", instance.crontab.day_of_week)
        cron_day_of_month = cron_data.get("day_of_month", instance.crontab.day_of_month)
        cron_month_of_year = cron_data.get("month_of_year", instance.crontab.month_of_year)
        cron_str = "{0} {1} {2} {3} {4}".format(cron_minute,
                                                cron_hour,
                                                cron_day_of_week,
                                                cron_day_of_month,
                                                cron_month_of_year)

        instance_kwargs = json.loads(instance.kwargs)
        instance_kwargs["cron_str"] = cron_str

        crontab_obj,_ = CrontabSchedule.objects.get_or_create(minute=cron_minute,
                                                              hour=cron_hour,
                                                              day_of_week=cron_day_of_week,
                                                              day_of_month=cron_day_of_month,
                                                              month_of_year=cron_month_of_year,
                                                              timezone=CELERY_TIMEZONE)
        instance.crontab = crontab_obj

        validated_scan_args = validated_data.pop('scan_args')

        if "address_range" in validated_scan_args:
            instance_kwargs["address_range"] = validated_scan_args.get('address_range').split(',')
            instance_kwargs["version"] = ip_network(instance_kwargs["address_range"][0])._version

        if "target_port" in validated_scan_args:
            instance_kwargs["target_port"] = validated_scan_args.get('target_port')

        if "request_hexdump" in validated_scan_args:
            instance_kwargs["request_hexdump"] = validated_scan_args.get('request_hexdump')

        if "packets_per_second" in validated_scan_args:
            instance_kwargs["packets_per_second"] = validated_scan_args.get('packets_per_second')

        instance.kwargs = json.dumps(instance_kwargs)
        instance.save()
        return instance

    def create(self, validated_data):
        cron_data = validated_data.pop("crontab")
        cron_minute = cron_data.get("minute", "*")
        cron_hour = cron_data.get("hour", "*")
        cron_day_of_week = cron_data.get("day_of_week", "*")
        cron_day_of_month = cron_data.get("day_of_month", "*")
        cron_month_of_year = cron_data.get("month_of_year", "*")
        cron_str = "{0} {1} {2} {3} {4}".format(cron_minute,
                                                cron_hour,
                                                cron_day_of_week,
                                                cron_day_of_month,
                                                cron_month_of_year)

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
        kwargs["request_hexdump"] = validated_scan_args.pop('request_hexdump')
        kwargs["packets_per_second"] = validated_scan_args.pop('packets_per_second',
                                                               ZMAP_PACKETS_PER_SECOND)
        kwargs["cron_str"] = cron_str

        # set the IP address version
        kwargs["version"] = ip_network(kwargs["address_range"][0])._version

        periodic_task_obj = PeriodicTask.objects.create(crontab=crontab_obj,
                                                        name=name,
                                                        task=task,
                                                        kwargs=json.dumps(kwargs))
        return periodic_task_obj
