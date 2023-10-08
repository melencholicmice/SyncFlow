import stripe
from syncflow.utilities import  register_subscriber,MainClassMeta,SubscriberBase
from syncflow.settings import STRIPE_API_KEY
from celery import shared_task
import logging
logger = logging.getLogger("default_logger")

class InvoiceInsync(metaclass=MainClassMeta):
        pass

class InvoiceOutsync(metaclass=MainClassMeta):
        pass

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

        try:
            stripe.Invoice.delete(invoice_id)
        except stripe.error.StripeError as e:
            logger.error(f"Error updating customer: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating customer: {e}")












