from .models import Order
from .utils import send_whatsapp_message
from django.utils import timezone

def cleanup_expired_orders():
    # Find orders where the expiration date has passed and they haven't been picked up
    expired_orders = Order.objects.filter(
        order_expiration_date__lte=timezone.now().date(),
        is_picked_up=False
    )
    
    # Optional: Send a 'sorry' message before deleting
    for order in expired_orders:
        msg = f"As you did not pick up your shoes, your order for {order.shoe.sku_id} has expired and the reservation has been released. 🛒"
        send_whatsapp_message(order.customer.phone_number, msg)
    
    # Delete them from the database
    expired_orders.delete()