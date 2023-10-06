from django.db import models
import uuid

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
            print(f"======> Creating a new customer: {self.name}")
        else:
            print(f"=======> Updating customer: {self.name}")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        print(f"Deleting record: {self.id}")
        super().delete(*args, **kwargs)


