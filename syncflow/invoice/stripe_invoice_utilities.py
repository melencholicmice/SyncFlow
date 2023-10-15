import stripe
from syncflow.sync_framework import  register_subscriber,SubscriberBase
from syncflow.settings import STRIPE_API_KEY
from celery import shared_task
import logging
logger = logging.getLogger("default_logger")
from syncflow.sync_framework import InvoiceOutsync


@register_subscriber(main_class=InvoiceOutsync)
class StripeInvoiceSubscriber(SubscriberBase):
    API_KEY = STRIPE_API_KEY

    field_to_key_mapping = {
        'id':'id',
        'customer_name' : 'customer_name',
        'customer_email':'customer_email'
    }

    @staticmethod
    @shared_task
    def create(**kwargs):
        raw_params = kwargs.get('raw_params')
        customer_id = raw_params.get('id')
        try:
            stripe.Invoice.create(
                customer=customer_id,
                api_key=STRIPE_API_KEY
            )
        except stripe.error.StripeError as e:
            logger.error(f"Error creating Invoice: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating Invoice: {e}")

    @staticmethod
    @shared_task
    def delete(**kwargs):
        raw_params = kwargs.get('raw_params')
        invoice_id = raw_params.get('id')
        print(invoice_id)
        try:
            stripe.Invoice.delete(invoice_id)
            print("tried deleting")
        except stripe.error.StripeError as e:
            logger.error(f"Error deleting customer: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting customer: {e}")












