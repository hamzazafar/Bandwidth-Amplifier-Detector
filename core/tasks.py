# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task
def scan(address_range, target_port, version):
    logger.info('Address Range: {0}  UDP Port: {1}  IP Version: {2}'
                .format(address_range, target_port, version))
