import os
from twilio.rest import Client

# You don't need django.setup() here! 
# Django is already running when this is called.

def send_whatsapp_message(to_number, body, media_url = None):
    # Load keys directly from the environment
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    # Ensure the number has the 'whatsapp:' prefix required by Twilio
    if not str(to_number).startswith('whatsapp:'):
        to_number = f'whatsapp:{to_number}'

    try:
        message = client.messages.create(
            body=body,
            from_=from_whatsapp,
            media_url=[media_url] if media_url else None,
            to=to_number
        )
        print(f"✅ Success! SID: {message.sid}")
        return True
    except Exception as e:
        print(f"❌ Error sending to {to_number}: {e}")
        return False

