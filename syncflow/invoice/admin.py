from django.contrib import admin
from .models import Invoice

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id','customer_name','customer_email')

admin.site.register(Invoice,InvoiceAdmin)
