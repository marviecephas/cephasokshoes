from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from .agent import run_agent_turn
import time
from .utils import send_whatsapp_message 
from django.shortcuts import render
from django.utils import timezone
from .models import Shoe, Customer, Order

def custom_404(request, exception):
    return render(request, '404.html', status=404)


def record_manual_sale(sku, category, size, total_price, paid, phone_number, customer_name=None):
    

    # 1. Handle the Shoe first (Create it if your dad hasn't yet)
    cleaned_sku = sku.strip()
    cleaned_number = f'+234{phone_number.strip()[1:]}' if (phone_number[0] == '0') else phone_number.strip()
    
    if not cleaned_sku:
        shoe_obj = Shoe.objects.create(
            category=category,
            size=size,
            price=total_price,
            status='sold' # Use your 'sold' value
        )
    else:
        # If a SKU IS provided, find it or create it
        shoe_obj, _ = Shoe.objects.update_or_create(
            sku_id=cleaned_sku,
            defaults={
                'category': category,
                'size': size,
                'price': total_price,
                'status': 'sold',
            }
        )
        shoe_obj.save()

    # 2. Now handle the Customer
    customer_obj, _ = Customer.objects.get_or_create(
        phone_number=cleaned_number,
        defaults={'name': customer_name}
    )
    customer_obj.save()

    # 3. Create the Order (This handles the "Owing" math)
    order = Order.objects.create(
        customer=customer_obj,
        shoe=shoe_obj,
        total_cost=total_price,
        amount_paid=paid,
        is_picked_up = True,
    )
    
    return order
session_memory = {}
SESSION_TIMEOUT = 14400

def manual_sale_view(request):
    if request.method == 'POST':
        # This handles the form data and triggers your existing record_manual_sale logic
        sku = request.POST.get('sku')
        category = request.POST.get('category')
        size = request.POST.get('size')
        total_price = request.POST.get('total_price')
        paid = request.POST.get('paid')
        phone = request.POST.get('phone_number')
        name = request.POST.get('customer_name')

        # Call the logic you built earlier
        record_manual_sale(sku, category, size, total_price, paid, phone, name)
        
        return redirect('/admin/business-dashboard/')
    return render(request, 'shop/manual_sale.html')

@csrf_exempt
def whatsapp_webhook(request):
    # 1. Capture the metadata from Twilio
    
    current_domain = request.build_absolute_uri('/')[:-1] # e.g., https://xyz.trycloudflare.com
    sender = request.POST.get('From', '') # e.g., 'whatsapp:+2347026373047'
    user_msg = request.POST.get('Body', '')
    print(f'user_msg = {user_msg}')
    current_time = time.time()

    # 2. Handle Session Initialization/Reset
    is_new_session = False
    if sender in session_memory:
        if (current_time - session_memory[sender]["last_active"]) > SESSION_TIMEOUT:
            is_new_session = True
    else:
        is_new_session = True

    if is_new_session:
        # INJECT IDENTITY: We tell the AI who the user is silently
        session_memory[sender] = {
            "messages": [
                {
                    "role": "user", 
                    "parts": [{"text": f"SYSTEM: The customer phone is {sender}. You are the warm assistant for Cephas OK Shoes. Do not ask for the phone number."}]
                },
                {
                    "role": "model", 
                    "parts": [{"text": "Hello! I am the Cephas OK Shoes assistant. How can I be of help to you today? 😊"}]
                }
            ],
            "last_active": current_time
        }
        
        # Immediate warm response for greetings to save API quota
        if user_msg.lower() in ['hello', 'hi', 'hey', 'ndewo', 'kedu']:
            twiml_resp = MessagingResponse()
            twiml_resp.message("Hello! I am the Cephas OK Shoes assistant. How can I be of help to you today? 😊")
            return HttpResponse(str(twiml_resp), content_type='application/xml')

    # 3. Standard Multi-turn logic
    session_memory[sender]["messages"].append({"role": "user", "parts": [{"text": user_msg}]})
    session_memory[sender]["last_active"] = current_time
    
    # AI now "sees" the phone number in history and won't ask for it
    ai_reply_text = run_agent_turn(session_memory[sender]["messages"], current_domain)

    session_memory[sender]["messages"].append({"role": "model", "parts": [{"text": ai_reply_text}]})

    # 4. Return TwiML to Twilio
    
    
    send_whatsapp_message(sender, ai_reply_text)
    return HttpResponse(status = 200)
    