import os
import sys
import subprocess
import django

sys.path.append(os.getcwd())
# Tell Python where your settings file is located
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# "Start" Django
django.setup()

from shop.models import Shoe, Customer
from twilio.rest import Client
from django.conf import settings

def run_check():
    print("--- 🛡️ Cephas OK Shoes System Health Check ---")
    
    # 1. Database Check
    try:
        shoe_count = Shoe.objects.count()
        cust_count = Customer.objects.count()
        print(f"✅ Database: Online ({shoe_count} shoes, {cust_count} customers)")
    except Exception as e:
        print(f"❌ Database: Error ({e})")

    # 2. Twilio Check
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
        print("✅ Twilio API: Credentials Valid")
    except Exception:
        print("❌ Twilio API: Connection Failed (Check keys/internet)")

    # 3. Cron Service Check
    cron_check = subprocess.run(['pgrep', 'crond'], capture_output=True)
    if cron_check.returncode == 0:
        print("✅ Cron Service: Running in background")
    else:
        print("❌ Cron Service: NOT RUNNING (Type 'crond' to start)")

if __name__ == "__main__":
    run_check()