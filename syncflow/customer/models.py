from django.db import models
import uuid
from .stripe_utilities import CustomerCRUD

class Customer(models.Model):
    id = models.UUIDField(
        primary_key=True,
        editable=False
    )

    name = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = uuid.uuid4()
            CustomerCRUD.create_customer(instance=self)
        else:
            original = Customer.objects.get(id=self.id)
            # Compare field values to detect updates
            updated_fields = {}
            for field in self._meta.fields:
                field_name = field.name
                old_value = getattr(original, field_name)
                new_value = getattr(self, field_name)

                if old_value != new_value:
                    updated_fields[field_name] = new_value
            # Do something with the updated_fields list (e.g., log or perform actions)
            if updated_fields:
                print("Updated fields:", updated_fields)
            CustomerCRUD.update_customer(original_fields=original, updated_params = updated_fields)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        CustomerCRUD.delete_customer(instance=self)
        super().delete(*args, **kwargs)

