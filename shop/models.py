from django.db import models
from django.utils import timezone
from datetime import timedelta
from .utils import send_whatsapp_message
import re

class Customer(models.Model):
    # Use CharField for phone numbers; TextField is unnecessarily large
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    
    # Most customers wear one size usually; let's store that
    preferred_lang = models.TextField(null = True, blank = True)
        
    def save(self, *args, **kwargs):
        # 1. Remove all non-numeric characters first
        nums_only = re.sub(r'\D', '', self.phone_number)
        
        # 2. Handle Nigerian local format (e.g., 070...)
        if nums_only.startswith('0') and len(nums_only) == 11:
            self.phone_number = '+234' + nums_only[1:]
        
        # 3. Handle numbers that start with 234 but lack the +
        elif nums_only.startswith('234') and len(nums_only) >= 13:
            self.phone_number = '+' + nums_only
            
        # 4. Fallback: if it's already +234..., keep it, otherwise add +
        else:
            if not self.phone_number.startswith('+'):
                self.phone_number = '+' + nums_only
            else:
                self.phone_number = '+' + nums_only # Re-clean to be safe
        
        if self.pk is None:
            if Customer.objects.filter(phone_number=self.phone_number).exists():
                # If it exists, we just stop here. 
                # This prevents the IntegrityError crash.
                return  
        
        super().save(*args, **kwargs)
     
    def __str__(self):
        return self.name if self.name else self.phone_number

class Shoe(models.Model):
    GENDER = [('m', 'male'), ('f', 'female'), ('n', 'neutral')]
    SHOES_CATEGORY = [
        ('cor', 'corporate'), ('can', 'canvas'), 
        ('des', 'designers'), ('san', 'sandals'), ('bts', 'boots'),
    ]
    SHOE_STATUS = [('avl', 'available'), ('sold', 'sold')]

    sku_id = models.CharField(max_length=50, unique=True, primary_key=True)
    gender = models.CharField(max_length=1, choices=GENDER, default='n')
    category = models.CharField(max_length=4, choices=SHOES_CATEGORY, default='can')
    size = models.PositiveIntegerField(default=0)
    # DecimalField must have these two arguments
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=SHOE_STATUS, default='avl')
    image = models.ImageField(upload_to='', null=True, blank=True)
    
    # This identifies if the shoe was created automatically for a manual sale
    is_ghost_entry = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sku_id}({self.get_status_display()})"
        
    def save(self, *args, **kwargs):
    # If it's a new shoe and we don't have a SKU yet
        if not self.sku_id:
            import uuid
            prefix = self.category[:3].upper() if self.category else "SHOE"
        # Use a short UUID suffix so it's unique but pretty from the start
            suffix = uuid.uuid4().hex[:4].upper()
            self.sku_id = f"{prefix}-{suffix}"
    
    # 2. The ONLY save call
    # This works for brand new shoes AND updates (like setting to 'sold')
        super().save(*args, **kwargs)
          

class Order(models.Model):
    PAYMENT_STATUS = [('o', 'owing'), ('p', 'paid')]
    
    # Changed to ForeignKey so 1 customer can have many orders
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE)
    
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS)
    
    date_ordered = models.DateField(default=timezone.now)
    # Auto-calculate expiration (e.g., 30 days for debt)
    order_expiration_date = models.DateField(null=True, blank=True)
    is_picked_up = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remember the status when loaded from database
        self._initial_pickup_status = self.is_picked_up
   
    def save(self, *args, **kwargs):
        is_new = self.pk is None
    
    # 1. Logic for cost and payment status
        cost = self.total_cost or 0
        paid = self.amount_paid or 0
        self.payment_status = 'o' if cost > paid else 'p'

        if not self.order_expiration_date:
            self.order_expiration_date = timezone.now().date() + timedelta(days=8)
        if not self.total_cost and self.shoe:
            self.total_cost = self.shoe.price

    # --- NEW ORDER PLACED ---
        if not self.pk:  # Only check when creating a NEW order
            duplicate_exists = Order.objects.filter(
            customer=self.customer,
            shoe=self.shoe,
            is_picked_up=False
        ).exists()
        
            if duplicate_exists:
            # Send a notification to the customer instead of just crashing
              msg = f"Hold on! ✋ You already have a pending order for these shoes ({self.shoe.sku_id}). No need to order twice! 😉"
              send_whatsapp_message(self.customer.phone_number, msg)
            
            # This prevents the order from being saved to the database
              return
        if is_new:
        # Send initial confirmation to the person who just ordered
            initial_msg = f"Order received for {self.shoe.sku_id}! 👟 Please ensure to pick the shoes up immediately as they may be sold before you come pick them up. We'll notify you if so."
            send_whatsapp_message(self.customer.phone_number, initial_msg)

        # Notify OTHER people who have active orders for this same shoe
            other_pending_orders = Order.objects.filter(shoe=self.shoe, 
            is_picked_up=False).exclude(customer=self.customer)

            for other in other_pending_orders:
                alert_msg = f"Another customer just placed an order for the same shoes ({self.shoe.sku_id})👟. Hurry and Pick them up now before they're gone!"
                send_whatsapp_message(other.customer.phone_number, alert_msg)

    # --- SHOE PICKED UP ---
        if self.is_picked_up and not getattr(self, '_initial_pickup_status', False):
        # Update the actual shoe status
            if self.shoe.status != 'sold':
                self.shoe.status = 'sold'
                self.shoe.save(update_fields=['status'])

        # Notify the person who actually bought it
            winner_msg = f"Oshey! 🙌 Thank you for picking up your shoes (Ref: {self.shoe.sku_id}). We hope you love them! 😊"
            send_whatsapp_message(self.customer.phone_number, winner_msg)

        # Notify and Delete/Cancel competing orders
            competing_orders = Order.objects.filter(shoe=self.shoe).exclude(pk=self.pk)
            for competitor in competing_orders:
                sold_out_msg = f"Sold Out! The shoes ({self.shoe.sku_id})👟 you ordered have been picked up by another customer. Please check out other shoes or stay tuned for our next restock!"
                send_whatsapp_message(competitor.customer.phone_number, sold_out_msg)
        
            competing_orders.delete()
            self._initial_pickup_status = True

        super().save(*args, **kwargs)  
    

    @property
    def balance(self):
        return self.total_cost - self.amount_paid
        
class ShoeRequest(models.Model):
    # Use ForeignKey so one customer can make multiple requests over time
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    requested_size = models.PositiveIntegerField()
    description = models.TextField()
    date_requested = models.DateTimeField(auto_now_add=True)
    fulfilled_by = models.ForeignKey('Shoe', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Request: Size {self.requested_size} for {self.customer.phone_number}"

class Content(models.Model):
    CONTENT_TYPE = [
        ('f', 'FUN_FACT'),
        ('t', 'HEALTH_TIP'),
    ]
    category = models.CharField(max_length=1, choices=CONTENT_TYPE)
    text_content = models.TextField() # Avoid naming a field 'content' inside a model named 'Content'

    def __str__(self):
        return f"{self.get_category_display()}: {self.text_content[:20]}..."
        
class NewStockAnnouncement(models.Model):
    date_triggered = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This helps your dad see a list of past broadcasts by date
        return f"Broadcast sent on {self.date_triggered.strftime('%b %d, %Y at %I:%M %p')}"

    def save(self, *args, **kwargs):
        # Check if it's a brand new entry
        if not self.id: 
            from .models import Customer
            from .utils import send_whatsapp_message
            
            # The exact message you wanted
            broadcast_msg = "🚀 NEW ARRIVALS ALERT! 🛍️ Just landed at Cephas Ok Shoes! 🔥 Fresh kicks, best prices! 👟👞 Check 'em out NOW! 😎"
            
            customers = Customer.objects.all()
            for customer in customers:
                send_whatsapp_message(customer.phone_number, broadcast_msg)
        
        super().save(*args, **kwargs)
        
