# Decorator for registering subscriber classes
import logging

logger = logging.getLogger('default_logger')

def register_subscriber(main_class):
    def decorator(subscriber_class):
        main_class.register(subscriber_class)
        return subscriber_class
    return decorator

class SubscriberBase:
    def __init__(self, name):
        self.name = name  # Common attribute for all subscribers

    def common_method(self):
        print(f"Common method for {self.name} subscriber")

    @classmethod
    def map_data_to_fields(cls, data):
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if key in data:
                mapped_data[field] = data[key]
        return mapped_data

    @classmethod
    def map_fields_to_data(cls, data):
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if field in data:
                mapped_data[key] = data[field]
        return mapped_data

# main function of this meta class is to maintian a list of subscribe classes
class MainClassMeta(type):
    subscribers = []

    def register(cls, subscriber_class):
        cls.subscribers.append(subscriber_class)

    @classmethod
    def call_subscriber_method(cls, method_name, *args, **kwargs):
        unsubscribe = []

        try:
            kwargs.get('unsubscribe')
        except:
            pass

        def is_shared_task(method):
            return hasattr(method, 'delay') if callable(method) else False

        for subscriber_class in cls.subscribers:
            if subscriber_class in unsubscribe:
                continue

            method = getattr(subscriber_class, method_name, None)
            if not method:
                continue

            if is_shared_task(method):
                try:
                    # Push the shared task to the Celery queue
                    task_result = method.delay(*args, **kwargs)
                    # You can handle the task result here or return it
                except Exception as e:
                    # Handle exceptions (e.g., log or add to a dead letter queue)
                    print(f"Error queuing shared task: {e}")
            else:
                # Not a shared task, so just execute the function
                print(f"Called without shared {method}")
                method(*args, **kwargs)

    @classmethod
    def create(cls, raw_params, unsubscribe=None):
        cls.call_subscriber_method('create', raw_params=raw_params, unsubscribe=unsubscribe)

    @classmethod
    def update(cls, original_params, updated_params, unsubscribe=None):
        cls.call_subscriber_method('update', original_params=original_params, updated_params=updated_params, unsubscribe=unsubscribe)

    @classmethod
    def delete(cls, raw_params, unsubscribe=None):
        cls.call_subscriber_method('delete', raw_params=raw_params, unsubscribe=unsubscribe)

class Insync(metaclass=MainClassMeta):
    pass

class Outsync(metaclass=MainClassMeta):
    pass
