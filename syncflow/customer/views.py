import json
import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from syncflow.settings import STRIPE_API_KEY
from .models import Customer


endpoint_secret = 'whsec_mHo6G7YDvJhx7eifYizkrhhwPGTPKuww'


@csrf_exempt
def stripe_webhook(request):
    print("===> Running")
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
        )


        if event.type == 'customer.created':
            print(f"customer.created\n{event}\n")
            name = event.data.object.name
            email = event.data.object.email
            cust = Customer.objects.create(
                name = name,
                email = email
            )

            cust.save()


        elif event.type == 'customer.deleted':
            print(f"customer.deleted\n{event}\n")
            name = event.data.object.name
            email = event.data.object.email
            obj_to_delete = Customer.objects.filter(name = name,email=email).first()
            obj_to_delete.delete()
            print("Deleted")

        elif event.type == 'customer.updated':
            print(f"customer.updated\n{event}\n")

        return HttpResponse(status=200)

    except ValueError as e:
        # Invalid payload
        print('Error parsing payload: {}'.format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print('Error verifying webhook signature: {}'.format(str(e)))
        return HttpResponse(status=400)

