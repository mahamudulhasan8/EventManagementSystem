from django.db import transaction
from django.utils import timezone
from apps.events.models import EventStatus, Event
from apps.tickets.models import TicketType
from apps.coupons.models import Coupon
from apps.common.exceptions import ApplicationError
from .models import Order, OrderItem
from django.conf import settings

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(user, event_id, items_data, coupon_code=None):
        """
        Creates an order with atomic locking to prevent race conditions on ticket inventory.
        items_data format: [{'ticket_type_id': uuid, 'quantity': int}]
        """
        # 1. Validate event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise ApplicationError("Event not found.")
            
        if event.status not in [EventStatus.PUBLISHED, EventStatus.ONGOING]:
            raise ApplicationError("Event is not currently active.")
            
        now = timezone.now()
        if now < event.registration_start or now > event.registration_end:
            raise ApplicationError("Registration is not currently open for this event.")
            
        # 2. Lock Ticket Types and validate availability
        ticket_type_ids = [item['ticket_type_id'] for item in items_data]
        
        # select_for_update() locks these rows until transaction ends
        ticket_types = TicketType.objects.select_for_update().filter(
            id__in=ticket_type_ids,
            event=event,
            is_active=True
        )
        
        if len(ticket_types) != len(ticket_type_ids):
            raise ApplicationError("One or more ticket types are invalid or unavailable.")
            
        ticket_type_map = {str(t.id): t for t in ticket_types}
        
        subtotal = 0
        order_items_to_create = []
        
        for item in items_data:
            tt_id = str(item['ticket_type_id'])
            qty = item['quantity']
            
            if qty <= 0:
                raise ApplicationError("Quantity must be greater than zero.")
                
            ticket_type = ticket_type_map[tt_id]
            
            # Validate max per order
            if qty > ticket_type.max_per_order:
                raise ApplicationError(f"Cannot order more than {ticket_type.max_per_order} of {ticket_type.name}.")
                
            # Validate inventory
            if ticket_type.available_quantity < qty:
                raise ApplicationError(f"Not enough tickets available for {ticket_type.name}. Only {ticket_type.available_quantity} left.")
                
            item_total = ticket_type.price * qty
            subtotal += item_total
            
            order_items_to_create.append({
                'ticket_type': ticket_type,
                'quantity': qty,
                'unit_price': ticket_type.price,
                'total_price': item_total
            })
            
            # Update sold quantity
            ticket_type.sold_quantity += qty
            ticket_type.save()
            
        # 3. Apply Coupon
        discount = 0
        coupon = None
        if coupon_code:
            try:
                # Lock coupon to safely update used_count
                coupon = Coupon.objects.select_for_update().get(code=coupon_code)
                is_valid, msg = coupon.is_valid(order_amount=subtotal)
                if not is_valid:
                    raise ApplicationError(msg)
                
                discount = coupon.calculate_discount(subtotal)
                coupon.used_count += 1
                coupon.save()
            except Coupon.DoesNotExist:
                raise ApplicationError("Invalid coupon code.")
                
        # 4. Calculate Taxes and Fees
        discounted_amount = subtotal - discount
        
        from decimal import Decimal
        tax_rate = Decimal(str(getattr(settings, 'TAX_RATE', 0)))
        fee_rate = Decimal(str(getattr(settings, 'SERVICE_FEE_RATE', 0)))
        
        tax = discounted_amount * tax_rate
        service_fee = discounted_amount * fee_rate
        total = discounted_amount + tax + service_fee
        
        # 5. Create Order
        order = Order.objects.create(
            user=user,
            event=event,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            service_fee=service_fee,
            total=total,
            coupon=coupon
        )
        
        # 6. Create Order Items
        for item_data in order_items_to_create:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
            
        return order
