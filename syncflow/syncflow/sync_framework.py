import logging

logger = logging.getLogger('default_logger')

'''
- Decorator for registering subscriber classes in a main_class
- Easy way to add any class to subscriber list
- pass the class to which you want to subscribe our class to in decorator argument (@main_call)

    @register_subscriber(main_class=MainClass)
    class SubscriberClass:
'''
def register_subscriber(main_class):
    def decorator(subscriber_class):
        print("Registering class")
        # Register the subscriber class with the main class
        main_class.register(subscriber_class)
        return subscriber_class
    return decorator

'''
- Subscriber Base class to provide utilities to common to all subscribers
'''
class SubscriberBase:
    def __init__(self, name):
        self.name = name  # Common attribute for all subscribers

    def common_method(self):
        print(f"Common method for {self.name} subscriber")

    @classmethod
    def map_data_to_fields(cls, data):
        '''
            convert data recived from API to django model recognisable
        '''
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if key in data:
                mapped_data[field] = data[key]
        return mapped_data

    @classmethod
    def map_fields_to_data(cls, data):
        '''
            convert data recived from django model to external API recogisable
        '''
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if field in data:
                mapped_data[key] = data[field]
        return mapped_data

'''
- meta class for Main class that stores list of subscriber
'''
class MainClassMeta(type):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        cls.subscribers = []  # Create a subscribers list for each class

class MainClass(metaclass=MainClassMeta):
    '''
    Main class and provides utlities to call all the subscribed class
    - has standard create,delete and update functionality that can be overidden
    - had a register method to add classes to its list
    '''

    @classmethod
    def call_subscriber_method(cls, method_name, *args, **kwargs):
        """
            Calls only the subscribed classes methods and ignores others
            put classes that you want to unsubscribe in an array and pass it
            also pushes those function into queue that have @shared_task decorator in it
        """
        unsubscribe = kwargs.get('unsubscribe')
        if unsubscribe is None:
            unsubscribe = []

        def is_shared_task(method):
            # Check if a method is a shared task
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
                    # Handle the task result as needed
                except Exception as e:
                    # Handle exceptions (e.g., log or add to a dead letter queue)
                    logger.error(f"Error queuing shared task: {e}")
            else:
                # Not a shared task, so just execute the function
                logger.info(f"Called without shared {method}")
                method(*args, **kwargs)


    @classmethod
    def register(cls, subscriber_class):
        # Register a subscriber class with the main class
        cls.subscribers.append(subscriber_class)


    @classmethod
    def create(cls, raw_params, unsubscribe=None):
        # Call the 'create' method for subscribers associated with this main class
        cls.call_subscriber_method('create', raw_params=raw_params, unsubscribe=unsubscribe)

    @classmethod
    def update(cls, original_params, updated_params, unsubscribe=None):
        # Call the 'update' method for subscribers associated with this main class
        cls.call_subscriber_method('update', original_params=original_params, updated_params=updated_params, unsubscribe=unsubscribe)

    @classmethod
    def delete(cls, raw_params, unsubscribe=None):
        # Call the 'delete' method for subscribers associated with this main class
        cls.call_subscriber_method('delete', raw_params=raw_params, unsubscribe=unsubscribe)


"""
List of available MainClasses (MainClasses are classes that stores)

:NOTE: here two classes (one to handle inwards sync and other for outwards sync)
- They are created on the basis of functionality and can be further modified as pper requirements
- although you can use only one class to handle both insync and out sync but not recommended as it might cause confusion
"""

# MainClass responsibe for inwards syncing of customer data
class Insync(MainClass):
    pass

# MainClass responsibe for outwards syncing of customer data
class Outsync(MainClass):
    pass
# MainClass responsibe for inwards syncing of invoice data
class InvoiceInsync(MainClass):
    pass

# MainClass responsibe for outwards syncing of invoice data
class InvoiceOutsync(MainClass):
    pass


