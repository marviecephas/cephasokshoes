from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import random
from datetime import datetime, timedelta

def send_health_tips():
    from .models import Customer, Content
    from .utils import send_whatsapp_message
    
    tips = []
    for content in Content.objects.all():
      text = f'Did you know?\n{content.text_content}\n\n*cephasokshoes*' if content.category == 'f' else f'Shoe{content.text_content}\n\n*cephasokshoes*'
      tips.append(text)
    if not tips:
      print('No tip found in content table')
      return
    customers = Customer.objects.all()
    
    # Send tips...
    for c in customers:
        send_whatsapp_message(c.phone_number, random.choice(tips))

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    
    # Schedule every 5 days
    # To randomize time, we can update the trigger or use a jitter
    scheduler.add_job(
        send_health_tips, 
        'interval', 
        days=5, 
        start_date=datetime.now().replace(hour=10, minute=0),
        jitter=28800 # Adds up to 8 hours of randomness (10am - 6pm)
    )
    scheduler.start()
    