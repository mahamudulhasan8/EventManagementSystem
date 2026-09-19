from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'provider', 'amount', 'currency', 'status', 'transaction_id', 'created_at')
    list_filter = ('provider', 'status', 'currency', 'created_at')
    search_fields = ('transaction_id', 'order__order_number')
    readonly_fields = ('order', 'provider', 'amount', 'currency', 'gateway_response')
