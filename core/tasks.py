from __future__ import absolute_import, unicode_literals
from celery import shared_task

from celery.utils.log import get_task_logger

from subprocess import Popen, PIPE

from ipaddress import ip_network, ip_address

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

    logger.debug('Request: {0!r}'.format(self.request))
    logger.info(('Scan Name: {0}'
                 'Address Range: {1}'
                 'UDP Port: {2}'
                 'IP Version:{3}'
                 'Hex Dump: {4}').format(scan_name,
                                         address_range,
                                         target_port,
                                         version,
                                         request_hexdump))

    if version not in [4, 6]:
        raise ValueError("Invalid IP Address Version %s specified " % version)

    request_size = len(request_hexdump)*2;

    zmap_udp_probe = "udp" if version == 4 else "ipv6_udp"
    #addresses = ' '.join(address_range)

    amps = dict()

    for addr in address_range:
        logger.info("Scanning address range: %s" % addr)

        cmd = ('zmap '
               '-M {0} '
               '-p {1} '
               '--probe-args=hex:{2} '
               '-f {3} '
               '-r {4} '
               '--output-module={5} '
               '--output-filter={6} '
               '{7}').format(zmap_udp_probe,
                             str(target_port),
                             request_hexdump,
                             'saddr,udp_pkt_size,data',
                             str(packets_per_second),
                             'csv',
                             '"success = 1"',
                             addr)
        process = Popen(cmd,
                        shell=True,
                        stdout=PIPE,
                        stderr=PIPE)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise Exception(stderr)

        stdout = stdout.decode().split('\n')
        logger.info(stdout)

        logger.info(stderr.decode().split('\n'))

        for row in stdout[1:]:
            if not row:
                continue
            amplifier, response_size, response_data = row.split(',')
            if amplifier not in amps:
                amps[amplifier] = dict()
                amps[amplifier]["responses"] = list()
                amps[amplifier]["total_response_size"] = 0

                net = ip_network(addr)

                if ip_address(amplifier) not in net:
                    amps[amplifier]["unsolicited_response"] = True
                else:
                    amps[amplifier]["unsolicited_response"] = False

            amps[amplifier]["total_response_size"] += int(response_size)
            amps[amplifier]["amplification_factor"] = round(amps[amplifier]["total_response_size"]/request_size, 2)

            response = dict()
            response["response_hex_data"] = response_data
            response["response_size"] = int(response_size)

            amps[amplifier]["responses"].append(response)


    # filters the amps dict for hosts with BAF greater than 1
    amplifiers = { k:v for k,v in amps.items() if val["amplification_factor"]>1 }

    result= dict()
    result["scan_name"] = scan_name
    result["request_size"] = request_size
    result["active_amplifiers_count"] = len(amplifiers)
    result["amplifiers"] = amplifiers
    return result
