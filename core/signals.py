from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django_celery_results.models import TaskResult
from core.models.scan import ScanTimeSeriesResult, Amplifier
from datetime import date
from prettytable import PrettyTable

import json

@receiver(post_save, sender=TaskResult)
def create_result(sender, instance, created, *args, **kwargs):
    """
    add docs..
    """
    if not (instance and created):
        return

    # save a new timeseries record
    res = json.loads(instance.result)
    active_amplifiers_count = res["active_amplifiers_count"]
    scan_name = res["scan_name"]

    scan_result_obj = ScanTimeSeriesResult(scan_name=scan_name,
                                           active_amplifiers_count=active_amplifiers_count,
                                           scan_result=instance)
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
    from_email = 'hamza.zafar1993@gmail.com'
    to = '11bscshzafar@seecs.edu.pk'

    html_content = table.get_html_string()

    msg = EmailMultiAlternatives(subject, '', from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
