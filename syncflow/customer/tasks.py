from __future__ import absolute_import, unicode_literals
import time
from celery import shared_task

def push_to_queue(func):
    @shared_task
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
