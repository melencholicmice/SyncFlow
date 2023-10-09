from __future__ import absolute_import, unicode_literals
import time
from celery import shared_task

@shared_task
def add(x, y):
    # just for testing puposes
    print("execution started...")
    time.sleep(10)
    return x + y