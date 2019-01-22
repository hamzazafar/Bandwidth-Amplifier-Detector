from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask
from core.models.scan import ScanTimeSeriesResult, Amplifier
from datetime import date
from prettytable import PrettyTable

from core.utils import send_mail

import json

import logging

EMAIL_RECEIVE_HOSTS = getattr(settings, 'EMAIL_RECEIVE_HOSTS', None)
EMAIL_SENDER = getattr(settings, 'EMAIL_HOST_USER', None)

logger = logging.getLogger(__name__)

@receiver(post_save, sender=TaskResult)
def create_result(sender, instance, created, *args, **kwargs):
    """
    add docs..
    """
    try:
        if not (instance and created):
            return

        if instance.task_name != 'core.tasks.scan':
            logger.info("don't send emails for tasks other than scanning")
            return

        if not EMAIL_RECEIVE_HOSTS:
            raise ValueError("EMAIL_RECEIVE_HOSTS configuration not found")

        if not EMAIL_SENDER:
            raise ValueError("EMAIL_HOST_USER configuration not found")

        EMAIL_RECEIVE_HOSTS_LIST = EMAIL_RECEIVE_HOSTS.split(',')

        res = json.loads(instance.result)
        periodic_task = PeriodicTask.objects.get(name=res["scan_name"])
        if instance.status == 'SUCCESS':
            # save a new timeseries record
            active_amplifiers_count = res["active_amplifiers_count"]
            scan_name = res["scan_name"]

            scan_result_obj = ScanTimeSeriesResult(scan_name=scan_name,
                                                   active_amplifiers_count=active_amplifiers_count,
                                                   scan_result=instance,
                                                   status=instance.status,
                                                   periodic_task=periodic_task)
            scan_result_obj.save()

            for ip, details in res["amplifiers"].items():
                obj = Amplifier(address=ip,
                                response_size=details["response_size"],
                                amplification_factor=details["amplification_factor"],
                                scan=scan_result_obj)
                obj.save()

            # send email to administrator
            if active_amplifiers_count < 1:
                return

            table = PrettyTable()
            table.field_names = ["Amplifier", "Response Size", "Amplification Factor"]

            for ip, details in res["amplifiers"].items():
                table.add_row([ip, details["response_size"], details["amplification_factor"]])

            table.sortby = "Amplification Factor"
            # sort in descending order
            table.reversesort = True

            subject = "%d amplifiers found for scan '%s'" % (active_amplifiers_count, scan_name)
            html_content = table.get_html_string()
            send_mail(subject, EMAIL_SENDER, EMAIL_RECEIVE_HOSTS_LIST, html_content=html_content)

        elif instance.status == 'FAILURE':
            scan_name = instance.task_kwargs['scan_name']

            scan_result_obj = ScanTimeSeriesResult(scan_name=scan_name,
                                                   active_amplifiers_count=0,
                                                   scan_result=instance,
                                                   status=instance.status,
                                                   periodic_task=periodic_task)
            scan_result_obj.save()

            subject = "Scan '%s' has failed " % scan_name
            from_email = 'hamza.zafar1993@gmail.com'
            to = '11bscshzafar@seecs.edu.pk'

            content = "Exception Type: %s\n" % res["exc_type"]
            content += "Exception Message: %s\n" % res["exc_message"]
            content += "Exception Module: %s\n" % res["exc_module"]
            content += instance.traceback
            send_mail(subject, EMAIL_SENDER, EMAIL_RECEIVE_HOSTS_LIST, txt_content=content)

    except Exception as err:
        # log exception
        logger.error("%s" % err)

@receiver(post_delete, sender=ScanTimeSeriesResult)
def delete_task_result(sender, instance, *args, **kwargs):
    task_result = instance.scan_result
    task_result.delete()
