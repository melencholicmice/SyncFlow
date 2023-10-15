from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('email','name','id')

admin.site.register(Customer,CustomerAdmin)
