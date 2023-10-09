import stripe
from django.db import models
from customer.models import Customer
from syncflow.settings import STRIPE_API_KEY
import logging
logger = logging.getLogger("default_logger")
from syncflow.sync_framework import SubscriberBase
from .stripe_invoice_utilities import InvoiceOutsync,StripeInvoiceSubscriber
from uuid import uuid4
# Create your models here.

class Invoice(models.Model):

    '''
        default value is becuase if we cannot access DB through django-admin with primary key empty
        :NOTE: Default value is a temparary solution
        :TODO: Find a better solution for this
    '''
    id = models.CharField(
        primary_key=True,
        editable=False,
        max_length=64,
         default="something-that-cannot-be-id"
    )

    customer_name = models.CharField(
        max_length=255
    )

    customer_email = models.EmailField()

    def get_params(self,instance=None, *args, **kwargs, ):
        params = {}

        for field in self._meta.fields:
            field_name = field.name
            value = getattr(self, field_name)
            params[field_name] = value
        return params

    def save(self, *args, **kwargs):
        if self.id == "something-that-cannot-be-id":
            params = self.get_params()
            try:
                customers = stripe.Customer.list(
                    email=params['customer_email'],
                    api_key=STRIPE_API_KEY
                )

                if len(customers['data']) == 0:
                    logger.error(f"Customer with email {params['customer_email']} doesnt exist")
                    # :TODO: Find some way to show error message in admin pannel that invoice not saved
                    return

                cust_id = customers['data'][0]['id']

                new_invoice = stripe.Invoice.create(
                    customer=cust_id,
                    api_key=STRIPE_API_KEY
                )

                self.id = new_invoice['id']
                super().save(*args, **kwargs)

                InvoiceOutsync.create(
                    raw_params=customers,
                    unsubscribe=[StripeInvoiceSubscriber]
                )
            except stripe.error.StripeError as e:
                logger.error(f"Error creating customer: {e}")
                return
            except Exception as e:
                logger.error(f"Unexpected error creating customer: {e}")
                return
        else:
            print("exited")
            super().save(*args, **kwargs)



    def delete(self, *args, **kwargs):
        raw_params = self.get_params()
        super().delete(*args, **kwargs)
        InvoiceOutsync.delete(raw_params=raw_params)








