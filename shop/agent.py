TOOLS_DECLARATION = [
    {
        "name": "get_user_preferred_sizes",
        "description": "Retrieves a list of shoe sizes the customer has purchased in the past.",
        "parameters": {
        "type": "object",
        "properties": {
            "phone_number": {"type": "string"}
        },
        "required": ["phone_number"]
        }
    },
    {
        "name": "check_inventory",
        "description": "Searches for available shoes based on size, category, gender and phone_number.",
        "parameters": {
            "type": "object",
            "properties": {
                "size": {"type": "integer"},
                "gender": {"type": "string"},
                "category": {"type": "string"},
                "phone_number" : { "type" : "string"}
            },
            "required": ["size", "gender", "category", "phone_number"]
        }
    },
    {
        "name": "calculate_debt",
        "description": "Retrieves the total unpaid balance for a specific customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "get_preferred_lang",
        "description": "Gets the customer preferred language for better interaction",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"}
            },
            "required": ["phone_number"]
        }
    },
    {
        "name": "log_order_request",
        "description": "Creates a temporary 'Reserved' order for a specific shoe SKU.",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "sku_id": {"type": "string"}
            },
            "required": ["phone_number", "sku_id"]
        }
    },
    {
        "name": "save_user_preference",
        "description": "Updates the customer's preferred language (e.g., English, Pidgin, Yoruba).",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "lang": {"type": "string"}
            },
            "required": ["phone_number", "lang"]
        }
    },
    {
        "name": "update_customer_profile",
        "description": "Updates or fills in the 'Name' field for a customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "name": {"type": "string"}
            },
            "required": ["phone_number", "name"]
        }
    },
    {
        "name": "get_content",
        "description": "Fetches marketing content, fun facts, and health tips.",
        "parameters": {"type": "object", "properties": {}}
    },
    {
        "name": "update_shoe_request",
        "description": "Records interest in a shoe that is currently out of stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "description": {"type": "string"},
                "size": {"type": "integer"}
            },
            "required": ["phone_number", "description", "size"]
        }
    }
]

system_instructions = """ 
ROLE: Warm assistant for CEPHAS OK SHOES.
GOAL: Identify shoe type/size, check stock, and log orders.

CRITICAL LOGIC FLOW:
1. GREETING: Call 'get_preferred_lang' first. Greet ONCE per session.
2. SIZING: If size is missing, call 'get_user_preferred_sizes'. Ask: "I see you've bought sizes [X, Y] before. Use one of these or a new size?".
3. INVENTORY: Always call 'check_inventory' before promising a shoe.
   - MULTIPLE RESULTS: If >1 shoe is found, list each SKU and URL individually. Ask for the specific SKU ID.
   - OUT OF STOCK: Call 'update_shoe_request' IMMEDIATELY if result is empty.
4. COMPLAINTS: If user is unhappy, say: "I'm not authorized for complaints, but contact our shop at +2347066954930 and you'll be well attended to".
5. THANK YOU: Do NOT respond to "Thank you" or "Done" after an order is logged. End the chat.

FORBIDDEN:
- Do not guess SKU IDs.
- Do not assume gender.
"""
import os
import django
import requests
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 2. Imports
from shop import tools  # Import the actual Python functions
from shop.agent import TOOLS_DECLARATION # Import your tool descriptions

API_KEY = os.getenv("GOOGLE_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

def run_agent_turn(history: list, current_domain):
    payload = {
        "contents": history,
        "tools": [{"function_declarations": TOOLS_DECLARATION}],
        "system_instruction": {"parts": [{"text": system_instructions}]}
    }
    
    response = requests.post(URL, json=payload).json()

    # Safety check for Quota/Errors
    if 'candidates' not in response:
        print(f"DEBUG GOOGLE RESPONSE: {response}")
        return "Ah, sorry o. My brain is a bit tired. Please try again in a moment."

    if 'content' not in response['candidates'][0] or 'parts' not in response['candidates'][0]['content']:
        print(f"BLOCKAGE DETECTED: Finish Reason: {response['candidates'][0].get('finishReason')}")
        print(f"FULL RESPONSE: {response}")
        return "Ah, sorry o. My brain is a bit tired. Please try again in a moment."
    part = response['candidates'][0]['content']['parts'][0]

    if 'functionCall' in part:
        fn_name = part['functionCall']['name']
        fn_args = part['functionCall'].get('args', {})
        if fn_name == "check_inventory":
          fn_args["domain"] = current_domain
        print(f"--- AI running: {fn_name}(**{fn_args}) ---")
        
        # 1. Store the AI's intent to use the tool in history
        history.append({"role": "model", "parts": [part]})
        
        # 2. Execute the tool
        tool_to_call = getattr(tools, fn_name)
        result = tool_to_call(**fn_args)
        print(f" --- result : {result} --- ")
        
        # 3. Store the result in history
        history.append({
            "role": "function",
            "parts": [{
                "functionResponse": {
                    "name": fn_name,
                    "response": {"result": result}
                }
            }]
        })
        
        # 4. RECURSION: The AI now reviews the history + result
        return run_agent_turn(history, current_domain)
    
    else:
        # Final text response
        answer = part.get('text', '')
        print(f"[Agent]: {answer}")
        return answer

if __name__ == "__main__":
    run_test("How much do I owe? My phone is +2347066954930")