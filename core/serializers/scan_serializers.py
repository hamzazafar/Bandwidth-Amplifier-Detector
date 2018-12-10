from rest_framework import serializers

from core.models.scan import Scan

from .validators import *

class ScanSerializer(serializers.ModelSerializer):
    address_range = serializers.CharField(allow_blank=False,
                                          max_length=255,
                                          validators=[address_range_validator],
                                          required=True)

    target_port = serializers.IntegerField(validators=[port_number_validator],
                                           required=True)

    class Meta:
        model = Scan
        fields = '__all__'
        read_only_fields = ('version',)
