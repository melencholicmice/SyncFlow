# from .stripe_utilities import StripeCustomerSubscriber

# Decorator for registering subscriber classes
def register_subscriber(main_class):
    def decorator(subscriber_class):
        main_class.register(subscriber_class)
        return subscriber_class
    return decorator

# main function of this meta class is to maintian a list of subscribe classes
class MainClassMeta(type):
    def __init__(cls, name, bases, attrs):
        cls.subscribers = []
        super(MainClassMeta, cls).__init__(name, bases, attrs)

    def register(cls, subscriber_class):
        cls.subscribers.append(subscriber_class)


# @register_subscriber(StripeCustomerSubscriber)
class Insync(metaclass=MainClassMeta):
    @staticmethod
    def create(raw_params,unsubscribe=None):
        for subscriber_class in Insync.subscribers:
            print(subscriber_class)
            if unsubscribe != subscriber_class:
                subscriber_class.create(raw_params=raw_params)

    @staticmethod
    def update(raw_params,unsubscribe=None):
        for subscriber_class in Insync.subscribers:
            if unsubscribe != subscriber_class:
                subscriber_class.update(raw_params=raw_params)

    @staticmethod
    def delete(raw_params,unsubscribe=None):
        for subscriber_class in Insync.subscribers:
            if unsubscribe != subscriber_class:
                subscriber_class.delete(raw_params=raw_params)

class Outsync(metaclass=MainClassMeta):
    @staticmethod
    def create(raw_params):
        print(Outsync.subscribers)
        for subscriber_class in Outsync.subscribers:
            subscriber_class.create(raw_params=raw_params)

    @staticmethod
    def update(original_params,updated_params):
        for subscriber_class in Outsync.subscribers:
            subscriber_class.update(
                original_params=original_params,
                updated_params=updated_params
            )

    @staticmethod
    def delete(raw_params):
        for subscriber_class in Outsync.subscribers:
            subscriber_class.delete(raw_params=raw_params)
