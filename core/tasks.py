# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task


@shared_task
def add(x, y):
    print("Hi there!")
    return x + y

@shared_task
def testing():
    print("HELO")
    return 100
