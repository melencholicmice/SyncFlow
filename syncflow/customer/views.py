import stripe
import  logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from syncflow.settings import STRIPE_ENDPOINT_SECRET
from .models import Customer
from .stripe_utilities import StripeCustomerSubscriber
from syncflow.sync_framework import Insync
from .tasks import add
from invoice.models import Invoice
from invoice.stripe_invoice_utilities import StripeInvoiceSubscriber

endpoint_secret = str(STRIPE_ENDPOINT_SECRET)

logger = logging.getLogger('default_logger')

# Test view
def test(request):
    return HttpResponse(status=200)

@csrf_exempt
def stripe_webhook(request):

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Verify and construct the Stripe event from the payload
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid request, return a 400 Bad Request response
        return HttpResponse(status=400)

    try:
        if event.type == 'customer.created':
            try:
                field_params = StripeCustomerSubscriber.map_data_to_fields(event.data.object)
            except Exception as e:
                logger.error(f'Error in Stripe API data: {e}')
                return HttpResponse(status=400)

            # :TODO: find a more elegant way to implement this
            try:
                # Check if the Customer already exists
                Customer.objects.get(**field_params)
                logger.error('Object already exists, so ignore the request')
                return HttpResponse(status=200)
            except Customer.MultipleObjectsReturned:
                logger.error("Duplicate objects in the table")
                return HttpResponse(status=404)
            except Customer.DoesNotExist:
                # continue execution if object already doesnt exists
                pass

            # Create a new Customer instance
            cust = Customer.objects.create(**field_params)
            cust.save()

            # Trigger an inward synchronization
            # :NOTE: here we have unsubscribed StripeCustomerSubscriber as in stripe data was already updated
            Insync.create(
                raw_params=event.data.object,
                unsubscribe=[StripeCustomerSubscriber]
            )

        elif event.type == 'customer.deleted':
            field_params = StripeCustomerSubscriber.map_data_to_fields(event.data.object)
            try:
                obj_to_delete = Customer.objects.get(**field_params)
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
            except Customer.MultipleObjectsReturned:
                objects = Customer.objects.filter(**field_params)
                for obj in objects:
                    obj.delete()

                return HttpResponse(status=200)

            # Delete the Customer instance
            obj_to_delete.delete()

            # Trigger an inward synchronization
            Insync.delete(
                raw_params=event.data.object,
                unsubscribe=[StripeCustomerSubscriber]
            )

        elif event.type == 'customer.updated':
            updated_field_params = {}
            current_params = event['data']['object']
            previous_params = event['data']['previous_attributes']

            old_field_params = StripeCustomerSubscriber.map_data_to_fields(previous_params)
            current_field_params = StripeCustomerSubscriber.map_data_to_fields(current_params)

            for key in current_field_params:
                if key in old_field_params:
                    updated_field_params[key] = current_field_params[key]

            # :TODO: find more elegant way to find changes in event
            changes = 0
            for field, value in current_field_params.items():
                if field in old_field_params:
                    changes += 1

            if changes == 0:
                return HttpResponse(status=200)

            try:
                object_to_update = Customer.objects.get(**current_field_params)
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
            except Customer.MultipleObjectsReturned:
                logger.error("Incomplete data, multiple objects of the same type exist")
                return HttpResponse(status=404)

            for field, value in updated_field_params.items():
                setattr(object_to_update, field, value)
            object_to_update.save()

            # Trigger an inward synchronization
            Insync.update(
                original_params=current_field_params,
                updated_params=updated_field_params,
                unsubscribe=[StripeCustomerSubscriber],
            )

        elif event.type == 'invoice.created':
            params = event['data']['object']
            params['id'] = event['data']['object']['id']

            if Invoice.objects.filter(id=params['id']).exists():
                return HttpResponse(status=200)

            # Map Stripe invoice data to fields
            params = StripeInvoiceSubscriber.map_data_to_fields(params)

            # Create a new Invoice instance
            new_invoice = Invoice.objects.create(
                **params
            )
            new_invoice.save()

        elif event.type == 'invoice.deleted':
            id = event['data']['object']['id']
            try:
                obj_to_delete = Invoice.objects.get(id=id)
            except Invoice.DoesNotExist:
                obj_to_delete = None

            if obj_to_delete:
                # Delete the Invoice object
                obj_to_delete.delete()
        return HttpResponse(status=200)

    except ValueError as e:
        # Invalid payload, Error parsing payload
        logger.error(f'Error parsing payload: {e}')
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature, Error verifying webhook signature
        logger.error(f'Error verifying webhook signature: {e}')
        return HttpResponse(status=400)
