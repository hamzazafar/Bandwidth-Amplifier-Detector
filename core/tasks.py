from __future__ import absolute_import, unicode_literals
from celery import shared_task

from celery.utils.log import get_task_logger

from subprocess import Popen, PIPE

from celery import states

import random

logger = get_task_logger(__name__)

@shared_task(bind=True)
def scan(self, scan_name, address_range, target_port, version,
         request_hexdump, packets_per_second, cron_str=''):
    # set task status started
    self.update_state(state=states.STARTED,
                      meta={"task_name": self.name,
                            "scan_name": scan_name})

    logger.info('Request: {0!r}'.format(self.request))
    logger.info("""
                Scan Name: {0}
                Address Range: {1}
                UDP Port: {2}
                IP Version:{3}
                Hex Dump: {4}
                """.format(scan_name, address_range, target_port, version, request_hexdump))

    if version not in [4, 6]:
        raise ValueError("Invalid IP Address Version %s specified " % version)

    zmap_udp_probe = "udp" if version == 4 else "ipv6_udp"
    addresses = ' '.join(address_range)
    process = Popen(['zmap',
                     '-M', zmap_udp_probe,
                     '-p', str(target_port),
                     '--probe-args=hex:%s' % request_hexdump,
                     '-f', 'saddr,udp_pkt_size',
                     '-r', str(packets_per_second),
                     '--output-module=csv',
                     '--output-filter="success = 1"',
                     addresses,],
                     stdout=PIPE,
                     stderr=PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        raise Exception(stderr)

    #stdout = "saddr,udp_pkt_size\n"
    #num_amps = random.randint(1,10)
    #request_size = random.randint(20,60)

    request_size = len(request_hexdump)*2;
    #for i in range(num_amps):
    #    saddr = "%s.%s.%s.%s" % (random.randint(0,255),random.randint(0,255),
    #                             random.randint(0,255),random.randint(0,255))
    #    response_size = random.randint(70,10000)
    #    stdout += "%s,%s\n" % (saddr, response_size)

    logger.info(stdout)
    logger.info(stderr)

    amps = dict()
    data = stdout.decode().split('\n')
    for row in data[1:]:
        if not row:
            continue
        amplifier, response_size = row.split(',')
        if amplifier not in amps:
            amps[amplifier] = dict()
            amps[amplifier]["response_size"] = response_size
            amps[amplifier]["amplification_factor"] = round(int(response_size)/request_size,2)
        else:
            amps[amplifier]["response_size"] += response_size
            amps[amplifier]["amplification_factor"] = round(int(amps[amplifier]["response_size"])/request_size,2)

    result= dict()
    result["scan_name"] = scan_name
    result["request_size"] = request_size
    #result["active_amplifiers_count"] = num_amps
    result["active_amplifiers_count"] = len(amps)
    result["amplifiers"] = amps
    return result
