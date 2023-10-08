# Decorator for registering subscriber classes
import logging

logger = logging.getLogger('default_logger')

def register_subscriber(main_class):
    def decorator(subscriber_class):
        main_class.register(subscriber_class)
        return subscriber_class
    return decorator

# main function of this meta class is to maintian a list of subscribe classes
class MainClassMeta(type):
    subscribers = []
    def __init__(cls, name, bases, attrs):
        super(MainClassMeta, cls).__init__(name, bases, attrs)

    def register(cls, subscriber_class):
        cls.subscribers.append(subscriber_class)

    @classmethod
    def call_subscriber_method(cls, method_name, *args, **kwargs):
        for subscriber_class in cls.subscribers:
            if kwargs.get('unsubscribe') != subscriber_class:
                method = getattr(subscriber_class, method_name, None)
                if method and callable(method):
                    if hasattr(method, 'delay'):
                        try:
                            # Push the shared task to the Celery queue
                            task_result = method.delay(*args, **kwargs)
                            # You can handle the task result here or return it
                        except Exception as e:
                            # Handle exceptions (e.g., log or add to a dead letter queue)
                            print(f"Error queuing shared task: {e}")
                    else:
                        # not a shared task, so just execute the function
                        print(f"called without shared {method}")
                        method(*args, **kwargs)



class Insync(metaclass=MainClassMeta):
    @classmethod
    def create(cls, raw_params, unsubscribe=None):
        cls.call_subscriber_method('create', raw_params=raw_params, unsubscribe=unsubscribe)

    @classmethod
    def update(cls, raw_params, unsubscribe=None):
        cls.call_subscriber_method('update', raw_params=raw_params, unsubscribe=unsubscribe)

    @classmethod
    def delete(cls, raw_params, unsubscribe=None):
        cls.call_subscriber_method('delete', raw_params=raw_params, unsubscribe=unsubscribe)

class Outsync(metaclass=MainClassMeta):
    @classmethod
    def create(cls, raw_params):
        cls.call_subscriber_method('create', raw_params=raw_params)

    @classmethod
    def update(cls, original_params, updated_params):
        cls.call_subscriber_method('update', original_params=original_params, updated_params=updated_params)

    @classmethod
    def delete(cls, raw_params):
        cls.call_subscriber_method('delete', raw_params=raw_params)
