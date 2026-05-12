import random
from django.core.management.base import BaseCommand
from shop.models import Customer, Content
from shop.utils import send_whatsapp_message

class Command(BaseCommand):
    help = 'Sends a random fun fact to all customers'

    def handle(self, *args, **kwargs):
        # Fetch content filtered by 'fun_fact' type
        facts = Content.objects.filter(category='f')
        
        if not facts.exists():
            self.stdout.write("No fun facts found. Add some in the Admin first!")
            return

        # Pick one random fact and get all valid customers
        random_fact = random.choice(facts).text_content
        customers = Customer.objects.exclude(phone_number__isnull=True)
        
        for customer in customers:
            # Send the message using the utils helper
            message = f"👞\n *Did you know?* \n\n{random_fact}"
            send_whatsapp_message(customer.phone_number, message)
            
        self.stdout.write(f"Sent fun fact to {customers.count()} customers!")