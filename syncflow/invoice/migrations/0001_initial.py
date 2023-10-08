# Generated by Django 4.2.6 on 2023-10-08 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.CharField(editable=False, max_length=64, primary_key=True, serialize=False)),
                ('customer_name', models.CharField(max_length=255)),
                ('customer_email', models.EmailField(max_length=254)),
            ],
        ),
    ]
