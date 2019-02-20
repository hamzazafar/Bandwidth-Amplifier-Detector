from __future__ import absolute_import, unicode_literals
from celery import shared_task

from celery.utils.log import get_task_logger

from subprocess import Popen, PIPE

from django.conf import settings

from ipaddress import ip_network, ip_address

from celery import states

import random

ZMAP_COMMAND = getattr(settings, 'ZMAP_PATH', 'zmap')
IPV6_SRC_ADDR = getattr(settings, 'IPV6_SRC_ADDR', None)

logger = get_task_logger(__name__)

def is_unsolicited_response(alist, item):
    first = 0
    last = len(alist)-1

    while first<=last:
        midpoint = (first + last)//2
        if alist[midpoint] == item:
            return False
        else:
            if item < alist[midpoint]:
                last = midpoint-1
            else:
                first = midpoint+1
    return True

@shared_task(bind=True)
def scan(self, scan_name, address_range, target_port, version,
         request_hexdump, packets_per_second, cron_str=''):
    # set task status started
    self.update_state(state=states.STARTED,
                      meta={"task_name": self.name,
                            "scan_name": scan_name})

    logger.debug('Request: {0!r}'.format(self.request))
    logger.info('Scan "%s" has started\n' % scan_name)
    logger.info(('Scan Name: {0}\n'
                 'Address Range: {1}\n'
                 'UDP Port: {2}\n'
                 'IP Version:{3}\n'
                 'Hex Dump: {4}\n').format(scan_name,
                                         address_range,
                                         target_port,
                                         version,
                                         request_hexdump))

    if version not in [4, 6]:
        raise ValueError("Invalid IP Address Version %s specified " % version)

    request_size = len(request_hexdump)*2;

    zmap_udp_probe = "udp" if version == 4 else "ipv6_udp"

    amps = dict()

    cmd = ('{7} '
           '-M {0} '
           '-p {1} '
           '--probe-args=hex:{2} '
           '-f {3} '
           '-r {4} '
           '--output-module={5} '
           '--output-filter={6} ').format(zmap_udp_probe,
                                          str(target_port),
                                          request_hexdump,
                                          'saddr,daddr,ipid,ttl,sport,dport,udp_pkt_size,data',
                                          str(packets_per_second),
                                          'csv',
                                          '"success = 1"',
                                          ZMAP_COMMAND)

    if version == 4:
        addresses = ' '.join(address_range)
        cmd += addresses
    else:
        if IPV6_SRC_ADDR is None:
            raise Exception("IPV6_SRC_ADDR is not set in configuration")

        cmd += '--ipv6-source-ip=%s ' % IPV6_SRC_ADDR
        cmd += '--ipv6-target-file=- ')

    process = Popen(cmd,
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                    stdin=PIPE)

    logger.info("ZMap Command: %s" % cmd)
    stdout = ''
    stderr = ''
    if version == 4:
        stdout, stderr = process.communicate()
    else:
        addresses = ""
        for net in address_range:
            for host in ip_network(net):
                addresses += "%s\n" % str(host)

        stdout, stderr = process.communicate(input=addresses.encode())


    if process.returncode != 0:
        raise Exception(stderr.decode())

    stdout = stdout.decode()
    logger.info(stdout)

    logger.info(stderr.decode())

    scanned_addresses_list = [int(host) for net in address_range for host in ip_network(net).hosts()]
    scanned_addresses_list.sort()

    stdout = stdout.split('\n')
    for row in stdout[1:]:
        if not row:
            continue
        amplifier, daddr, ipid, ttl, sport, dport, response_size, response_data = row.split(',')
        if amplifier not in amps:
            amps[amplifier] = dict()
            amps[amplifier]["responses"] = list()
            amps[amplifier]["total_response_size"] = 0
            amps[amplifier]["destination_address"] = daddr

            amps[amplifier]["unsolicited_response"] = is_unsolicited_response(scanned_addresses_list, int(ip_address(amplifier)))

        amps[amplifier]["total_response_size"] += int(response_size)
        amps[amplifier]["amplification_factor"] = round(amps[amplifier]["total_response_size"]/request_size, 2)

        response = dict()
        response["response_ipid"] = int(ipid)
        response["response_ttl"] = int(ttl)
        response["response_sport"] = int(sport)
        response["response_dport"] = int(dport)
        response["response_hex_data"] = response_data
        response["response_size"] = int(response_size)

        amps[amplifier]["responses"].append(response)


    # filters the amps dict for hosts with BAF greater than 1
    amplifiers = { k:v for k,v in amps.items() if v["amplification_factor"]>1 }

    result= dict()
    result["scan_name"] = scan_name
    result["request_size"] = request_size
    result["active_amplifiers_count"] = len(amplifiers)
    result["amplifiers"] = amplifiers
    return result
