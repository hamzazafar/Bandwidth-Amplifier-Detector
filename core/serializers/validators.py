from rest_framework import serializers

from ipaddress import ip_network
from django_celery_beat.validators import *

import ast

def port_number_validator(value):
    """
    checks if the value is a valid port number
    """

    if not (1 <= value <= 65535):
        raise serializers.ValidationError('Port number must be in the range 1 to 65535')

    return value

def address_range_validator(value):
    """
    checks if the value is a valid IPv4/IPv6 address range in CIDR notation
    """
    address_range_list = value.split(",")

    ipv4_addr = False
    ipv6_addr = False
    for address_range in address_range_list:
        print("check %s" % address_range)
        if '/' not in address_range:
            raise serializers.ValidationError('Please provide address range %s in CIDR notation'
                                              % address_range)
        try:
            addr_range = ip_network(address_range)
            if addr_range._version == 4:
                ipv4_addr = True
            else:
                ipv6_addr = True

            if ipv4_addr and ipv6_addr:
                raise serializers.ValidationError('All address ranges should be IPv4 only or IPv6')

        except ValueError as err:
            raise serializers.ValidationError(err)

    return value

def cron_validator(validator, value):
    try:
        validator(value)
    except Exception as err:
        raise serializers.ValidationError(err.message)

    return value
