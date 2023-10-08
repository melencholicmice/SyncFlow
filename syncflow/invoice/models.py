import stripe
from django.db import models
from customer.models import Customer
from syncflow.settings import STRIPE_API_KEY
import logging
logger = logging.getLogger("default_logger")
from syncflow.utilities import SubscriberBase
from .stripe_invoice_utilities import InvoiceOutsync,StripeInvoiceSubscriber

# Create your models here.

class Invoice(models.Model):

    id = models.CharField(
        primary_key=True,
        editable=False,
        max_length=64
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
        if self.id is None:
            params = self.get_params()
            try:
                customers = stripe.Customer.list(
                    email=params['customer_email'],
                    api_key=STRIPE_API_KEY
                )

                if len(customers) > 0:
                    logger.info(f"Customer with email {params['customer_email']} already exists")
                    return

                customer_params = SubscriberBase.map_data_to_fields(data=params)

                new_customer = stripe.Customer.create(
                    **customer_params,
                    api_key=STRIPE_API_KEY
                )

                new_cust_id = new_customer['id']

                self.id = new_cust_id
                super().save(*args, **kwargs)
                customer_params['id'] = new_cust_id

                InvoiceOutsync.create(
                    raw_params=customer_params,
                    unsubscribe=[StripeInvoiceSubscriber]
                )


            except stripe.error.StripeError as e:
                logger.error(f"Error creating customer: {e}")
                return
            except Exception as e:
                logger.error(f"Unexpected error creating customer: {e}")
                return
        else:
            super().save(*args, **kwargs)



    def delete(self, *args, **kwargs):
        raw_params = self.get_params()
        super().delete(*args, **kwargs)

        InvoiceOutsync.delete(raw_params=raw_params)








