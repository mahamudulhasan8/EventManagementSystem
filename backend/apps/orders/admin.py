from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('ticket_type', 'quantity', 'unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'event', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email', 'event__title')
    readonly_fields = ('order_number', 'subtotal', 'discount', 'tax', 'service_fee', 'total')
    inlines = [OrderItemInline]
