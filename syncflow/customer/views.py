import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from syncflow.settings import STRIPE_ENDPOINT_SECRET
from .models import Customer
from .stripe_utilities import StripeCustomerSubscriber
from syncflow.utilities import Insync
from .tasks import add
from invoice.models import Invoice
from invoice.stripe_invoice_utilities import StripeInvoiceSubscriber

endpoint_secret = str(STRIPE_ENDPOINT_SECRET)

def test(request):
    return HttpResponse(status=200)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid request
        return HttpResponse(status=400)
    try:
        if event.type == 'customer.created':
            try:
                field_params = StripeCustomerSubscriber.map_data_to_fields(event.data.object)
            except Exception as e:
                print('Error in stripe api data: {}'.format(str(e)))
                return HttpResponse(status=400)
            try:
                Customer.objects.get(**field_params)
                print('Object already exists so ignore request')
                return HttpResponse(status=200)
            except Customer.MultipleObjectsReturned:
                print("dublicate objects in table")
                return HttpResponse(status=404)
            except Customer.DoesNotExist:
                pass


            cust = Customer.objects.create(**field_params)
            cust.save()

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


            obj_to_delete.delete()
            Insync.delete(
                raw_params=event.data.object,
                unsubscribe=[StripeCustomerSubscriber]
            )

        elif event.type == 'customer.updated':
            updated_field_params ={}
            current_params =event['data']['object']
            previous_params = event['data']['previous_attributes']

            old_field_params = StripeCustomerSubscriber.map_data_to_fields(previous_params)
            current_field_params = StripeCustomerSubscriber.map_data_to_fields(current_params)

            for key in current_field_params:
                if key in old_field_params:
                    updated_field_params[key] = current_field_params[key]

            # because stripe api just gives us previously changed fields and in some cases it might not be enough for uniquely identify an object
            grouped_params = {}
            changes = 0
            for field,value in current_field_params.items():
                if field  in old_field_params:
                    grouped_params[field] = old_field_params[field]
                    changes+=1
                else:
                    grouped_params[field] = value

            if changes == 0:
                print("no changes detected")
                return HttpResponse(status=200)

            # :TODO: Change it and make it inward sync with unsubscribed class
            try:
                object_to_update = Customer.objects.get(**grouped_params)
            except Customer.DoesNotExist:
                return HttpResponse(status=404)
            except Customer.MultipleObjectsReturned:
                print("Incomplete data , multiple objects of same type exists")
                return HttpResponse(status=404)

            for field, value in updated_field_params.items():
                setattr(object_to_update,field,value)
            object_to_update.save()

            Insync.update(
                raw_params=event.data.object,
                unsubscribe=[StripeCustomerSubscriber],
            )
        elif event.type == 'invoice.created':
            params = event['data']['object']
            params['id'] = event['data']['object']['id']

            if Invoice.objects.filter(id=params['id']).exists():
                return HttpResponse(status=200)

            params = StripeInvoiceSubscriber.map_data_to_fields(params)

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
                # Delete the object
                obj_to_delete.delete()
        return HttpResponse(status=200)

    except ValueError as e:
        # Invalid payload, Error parsing payload:
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)

