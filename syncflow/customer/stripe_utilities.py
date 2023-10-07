import stripe
from django.http import HttpResponse
from .utilities import  register_subscriber, Outsync,Insync
from syncflow.settings import STRIPE_API_KEY
from .tasks import push_to_queue

class SubscriberBase:
    def __init__(self, name):
        self.name = name  # Common attribute for all subscribers

    def common_method(self):
        print(f"Common method for {self.name} subscriber")

@register_subscriber(main_class=Outsync)
class StripeCustomerSubscriber(SubscriberBase):
    API_KEY = STRIPE_API_KEY  # Class-level variable to store the API key

    # Mapping between model fields and API data keys
    field_to_key_mapping = {
        'email': 'email',
        'name': 'name',
    }

    @classmethod
    def map_data_to_fields(cls, data):
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if key in data:
                mapped_data[field] = data[key]
        return mapped_data

    @classmethod
    def map_fields_to_data(cls,data):
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if field in data:
                mapped_data[key] = data[field]
        return mapped_data

    @staticmethod
    # @push_to_queue
    def create(**kwargs):
        if StripeCustomerSubscriber.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")

        raw_params = kwargs['raw_params']
        customer_params = StripeCustomerSubscriber.map_data_to_fields(data=raw_params)
        customers = []
        email = customer_params['email']
        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )
        except Exception as e:
            # :TODO: Handle the exception or add to a dead letter queue as needed
            # :TODO: fix status codes
            print(f"request rejected  because :- {e}")
            return HttpResponse(status=400)

        if len(customers) > 0:
            # customer already exists
            return HttpResponse(status=200)

        try:
            stripe.Customer.create(
                **customer_params,
                api_key=StripeCustomerSubscriber.API_KEY
            )
        except stripe.error.StripeError as e:
            # Handle the error or log it as needed
            print(f"Error because of stripe: {e}")
            return HttpResponse(status=500)
        except Exception as e:
            print(f"Error creating customer: {e}")
            return HttpResponse(status=500)


    @staticmethod
    # @push_to_queue
    def delete(**kwargs):
        if StripeCustomerSubscriber.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")

        raw_params = kwargs['raw_params']
        customer_params = StripeCustomerSubscriber.map_data_to_fields(data=raw_params)

        customers = []
        email = customer_params['email']
        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )
            customer_id = customers['data'][0]['id']
        except:
            # Handle the exception or add to a dead letter queue as needed
            #:TODO: fix status codes
            return HttpResponse(status=400)

        if len(customers) == 0:
            return HttpResponse(status=200)


        try:
            stripe.Customer.delete(
                customer_id,
                api_key=StripeCustomerSubscriber.API_KEY
            )
        except stripe.error.StripeError as e:
            # Handle the error or log it as needed
            print(f"Error deleting customer: {e}")
            return HttpResponse(status=500)

    @staticmethod
    # @push_to_queue
    def update(**kwargs):
        if StripeCustomerSubscriber.API_KEY is None:
            raise ValueError("API key is not set. Call initialize() first.")
        original_params = kwargs['original_params']

        email = original_params['email']
        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )
        except Exception as e:
            # :TODO: Handle the exception or add to a dead letter queue as needed
            # :TODO: fix status codes
            print(f"request rejected  because :- {e}")
            return HttpResponse(status=500)

        if not len(customers) == 1:
            if len(customers) > 1:
                return HttpResponse(status=200)
            return HttpResponse(status=404)

        customer_id = customers['data'][0]['id']
        update_params = kwargs["updated_params"]


        try:
            stripe.Customer.modify(
                customer_id,
                **update_params,  # Dictionary unpacking
                api_key=StripeCustomerSubscriber.API_KEY
            )
        except stripe.error.StripeError as e:
            # Handle the error or log it as needed
            print(f"Error updating customer: {e}")
