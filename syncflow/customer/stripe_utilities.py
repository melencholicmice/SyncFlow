import stripe
from .utilities import  register_subscriber, Outsync,Insync
from syncflow.settings import STRIPE_API_KEY
from celery import shared_task
import logging
logger = logging.getLogger("default_logger")

class SubscriberBase:
    def __init__(self, name):
        self.name = name  # Common attribute for all subscribers

    def common_method(self):
        print(f"Common method for {self.name} subscriber")



@register_subscriber(main_class=Outsync)
class StripeCustomerSubscriber(SubscriberBase):
    API_KEY = STRIPE_API_KEY

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
    def map_fields_to_data(cls, data):
        mapped_data = {}
        for field, key in cls.field_to_key_mapping.items():
            if field in data:
                mapped_data[key] = data[field]
        return mapped_data

    @staticmethod
    @shared_task
    def create(**kwargs):
        raw_params = kwargs.get('raw_params')
        email = raw_params.get('email')

        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            if len(customers) > 0:
                logger.info(f"Customer with email {email} already exists")
                return

            customer_params = StripeCustomerSubscriber.map_data_to_fields(data=raw_params)

            stripe.Customer.create(
                **customer_params,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            logger.info(f"Customer with email {email} created successfully")
        except stripe.error.StripeError as e:
            logger.error(f"Error creating customer: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating customer: {e}")

    @staticmethod
    @shared_task
    def delete(**kwargs):
        raw_params = kwargs.get('raw_params')
        email = raw_params.get('email')

        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            if len(customers) == 0:
                logger.info(f"Customer with email {email} does not exist")
                return

            customer_id = customers['data'][0]['id']
            stripe.Customer.delete(
                customer_id,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            logger.info(f"Customer with email {email} deleted successfully")
        except stripe.error.StripeError as e:
            logger.error(f"Error deleting customer: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting customer: {e}")

    @staticmethod
    @shared_task
    def update(**kwargs):
        original_params = kwargs.get('original_params')
        email = original_params.get('email')

        try:
            customers = stripe.Customer.list(
                email=email,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            if len(customers) != 1:
                if len(customers) > 1:
                    logger.warning(f"Multiple customers found with email {email}")
                else:
                    logger.warning(f"No customer found with email {email}")
                return

            customer_id = customers['data'][0]['id']
            update_params = kwargs.get('updated_params')

            stripe.Customer.modify(
                customer_id,
                **update_params,
                api_key=StripeCustomerSubscriber.API_KEY
            )

            logger.info(f"Customer with email {email} updated successfully")
        except stripe.error.StripeError as e:
            logger.error(f"Error updating customer: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating customer: {e}")
