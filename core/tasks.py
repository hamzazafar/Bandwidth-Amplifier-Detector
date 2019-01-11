# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from celery.utils.log import get_task_logger

import random

logger = get_task_logger(__name__)

@shared_task(bind=True)
def scan(self, scan_name, address_range, target_port, version, request_hexdump,
         cron_str=''):
    logger.info('Request: {0!r}'.format(self.request))
    logger.info("""
                Scan Name: {0}
                Address Range: {1}
                UDP Port: {2}
                IP Version:{3}
                Hex Dump: {4}
                """.format(scan_name, address_range, target_port, version, request_hexdump))

    num_amps = random.randint(1,10)
    request_size = random.randint(20,60)
    amps = dict()
    for i in range(num_amps):
        ip = "%s.%s.%s.%s" % (random.randint(0,255),random.randint(0,255),
                              random.randint(0,255),random.randint(0,255))
        amps[ip] = dict()
        response_size = random.randint(30,10000)
        amps[ip]["response_size"] = response_size
        amps[ip]["amplification_factor"] = round(response_size/request_size,2)

    result= dict()
    result["scan_name"] = scan_name
    result["request_size"] = request_size
    result["active_amplifiers_count"] = num_amps
    result["amplifiers"] = amps
    return result
