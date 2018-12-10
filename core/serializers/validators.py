from rest_framework import serializers

from ipaddress import ip_network

def port_number_validator(value):
    """
    checks if the value is a valid port number
    """

    if not (1 <= value <= 65535):
        raise serializers.ValidationError('Port number must be in the range 1 to 65535')

def address_range_validator(value):
    """
    checks if the value is a valid IPv4/IPv6 address range in CIDR notation
    """

    if '/' not in value:
        raise serializers.ValidationError('Please provide address range in CIDR notation')

    try:
        ip_network(value)
    except ValueError as err:
        raise serializers.ValidationError(err)
