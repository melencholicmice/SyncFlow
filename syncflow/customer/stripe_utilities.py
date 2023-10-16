import stripe
from syncflow.sync_framework import  register_subscriber, Outsync, SubscriberBase ,Insync
from syncflow.settings import STRIPE_API_KEY
from celery import shared_task
import logging
logger = logging.getLogger("default_logger")
from .models import Customer
from django.http import HttpResponse



@register_subscriber(main_class=Outsync)
@register_subscriber(main_class=Insync)
class StripeCustomerSubscriber(SubscriberBase):
    API_KEY = STRIPE_API_KEY

    field_to_key_mapping = {
        'email': 'email',
        'name': 'name',
    }

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


