from django.db import models
from ipaddress import ip_network

class Scan(models.Model):

    address_range = models.CharField(max_length=255,
                                     default='',
                                     null=False)

    target_port = models.IntegerField(null=False)

    version = models.IntegerField(null=False)


    def save(self, *args, **kwargs):
        """
        overriding save method to set the version!
        """
        self.version = ip_network(self.address_range).version
        super(Scan, self).save(*args, **kwargs)
