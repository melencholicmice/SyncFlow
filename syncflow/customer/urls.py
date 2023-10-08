from django.urls import path, include
from . import views

customer_urls = [
    path("stripe_webhook", views.stripe_webhook, name="Stripe Webhook"),
    path("test", views.test, name="test endpoint"),
]