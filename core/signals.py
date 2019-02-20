from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask
from core.models.scan import ScanTimeSeriesResult, Amplifier, Response
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
        if not instance:
            return

        if instance.status in ["STARTED", "REVOKED"]:
            return

        if not EMAIL_RECEIVE_HOSTS:
            raise ValueError("EMAIL_RECEIVE_HOSTS configuration not found")

        if not EMAIL_SENDER:
            raise ValueError("EMAIL_HOST_USER configuration not found")

        EMAIL_RECEIVE_HOSTS_LIST = EMAIL_RECEIVE_HOSTS.split(',')

        res = json.loads(instance.result)
        if instance.status == 'SUCCESS':
            # save a new timeseries record
            active_amplifiers_count = res["active_amplifiers_count"]
            scan_name = res["scan_name"]

            periodic_task = PeriodicTask.objects.get(name=res["scan_name"])
            scan_result_obj = ScanTimeSeriesResult(scan_name=scan_name,
                                                   active_amplifiers_count=active_amplifiers_count,
                                                   scan_result=instance,
                                                   status=instance.status,
                                                   periodic_task=periodic_task)
            scan_result_obj.save()

            for ip, details in res["amplifiers"].items():
                amp_obj = Amplifier(address=ip,
                                    destination_address=details["destination_address"],
                                    total_response_size=details["total_response_size"],
                                    amplification_factor=details["amplification_factor"],
                                    unsolicited_response=details["unsolicited_response"],
                                    private_address=details["private_address"],
                                    scan=scan_result_obj)
                amp_obj.save()

                for response in details["responses"]:
                    res_obj = Response(response_hex_data=response["response_hex_data"],
                                       response_size=response["response_size"],
                                       response_ipid=response["response_ipid"],
                                       response_ttl=response["response_ttl"],
                                       response_sport=response["response_sport"],
                                       response_dport=response["response_dport"],
                                       amplifier=amp_obj)
                    res_obj.save()



            # send email to administrator
            if active_amplifiers_count < 1:
                return

            table = PrettyTable()
            table.field_names = ["Amplifier",
                                 "Response Size",
                                 "Amplification Factor",
                                 "Unsolicited Response",
                                 "Address Type"]

            for ip, details in res["amplifiers"].items():
                table.add_row([ip,
                               details["total_response_size"],
                               details["amplification_factor"],
                               details["unsolicited_response"],
                               details["private_address"]])

            table.sortby = "Amplification Factor"
            # sort in descending order
            table.reversesort = True

            subject = "%d amplifiers found for scan '%s'" % (active_amplifiers_count, scan_name)
            html_content = table.get_html_string()
            send_mail(subject, EMAIL_SENDER, EMAIL_RECEIVE_HOSTS_LIST, html_content=html_content)

        elif instance.status == 'FAILURE':
            scan_name = instance.task_kwargs['scan_name']

            periodic_task = PeriodicTask.objects.get(name=scan_name)
            scan_result_obj = ScanTimeSeriesResult(scan_name=scan_name,
                                                   active_amplifiers_count=0,
                                                   scan_result=instance,
                                                   status=instance.status,
                                                   periodic_task=periodic_task)
            scan_result_obj.save()

            subject = "Scan '%s' has failed " % scan_name

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
