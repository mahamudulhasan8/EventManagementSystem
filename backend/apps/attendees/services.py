from apps.orders.models import Order
from apps.attendees.models import Attendee

class AttendeeService:
    @staticmethod
    def generate_tickets_for_order(order: Order):
        """
        Generates Attendee records and QR codes for a completed order.
        """
        attendees = []
        for item in order.items.all():
            for _ in range(item.quantity):
                attendee = Attendee.objects.create(
                    user=order.user,
                    event=order.event,
                    ticket_type=item.ticket_type,
                    order_item=item
                )
                attendees.append(attendee)
        return attendees
