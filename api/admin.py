from django.contrib import admin

from .models import Payment, Organization, BalanceLog


admin.site.register(Payment)
admin.site.register(Organization)
admin.site.register(BalanceLog)