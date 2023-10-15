import json
import uuid
from django.db import models
from syncflow.sync_framework import Outsync


class Customer(models.Model):

    id = models.UUIDField(
        primary_key=True,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    def get_params(self, instance=None, *args, **kwargs):
        """
            Get the parameters of the Customer instance and convert it to dictinary.
            useful in passing parameters to  other APIs
        """
        params = {}
        for field in self._meta.fields:
            field_name = field.name
            value = getattr(self, field_name)

            if isinstance(value, uuid.UUID):
            # Convert UUID to a string to avoid error in serialisation
                value = str(value)

            params[field_name] = value

        return params

    def get_updated_fields(self, *args, **kwargs):
        """
            Identify updated fields in the Customer instance.
        """
        original = Customer.objects.get(id=self.id)
        updated_fields = {}
        original_params = {}

        for field in self._meta.fields:
            field_name = field.name
            old_value = getattr(original, field_name)
            new_value = getattr(self, field_name)
            if old_value != new_value:
                updated_fields[field_name] = new_value

            original_params[field_name] = old_value

        return (original_params, updated_fields)

    def save(self, *args, **kwargs):
        if self.id is None:
            # Generate a UUID if it's a new instance
            self.id = uuid.uuid4()
            super().save(*args, **kwargs)
            raw_params = self.get_params()
            Outsync.create(raw_params=raw_params)
        else:
            original_params, updated_params = self.get_updated_fields()
            super().save(*args, **kwargs)

            # Update the external system using Outsync
            Outsync.update(
                original_params=original_params,
                updated_params=updated_params
            )

    def delete(self, *args, **kwargs):
        raw_params = self.get_params()
        super().delete(*args, **kwargs)

        # Delete the record from the external system using Outsync
        Outsync.delete(raw_params=raw_params)
