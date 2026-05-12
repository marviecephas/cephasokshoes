import os
import django
import requests
import json
from dotenv import load_dotenv

# 1. Setup Django and Environment
load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# 2. Imports after setup
from shop import tools  # This allows getattr(tools, ...) to work
from shop.agent import TOOLS_DECLARATION, system_instructions

API_KEY = os.getenv("GOOGLE_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={API_KEY}"

def run_agent_turn(user_message):
    print(f"\n[User]: {user_message}")
    
    payload = {
        "contents": [{"parts": [{"text": user_message}]}],
        "tools": [{"function_declarations": TOOLS_DECLARATION}],
        "system_instruction": {"parts": [{"text": system_instructions}]}
    }

    # STEP 1: Ask Gemini what to do
    response = requests.post(URL, json=payload).json()
    
    try:
        # Get the first response part
        part = response['candidates'][0]['content']['parts'][0]
        
        # Check if Gemini wants to call a tool
        if 'functionCall' in part:
            call = part['functionCall']
            fn_name = call['name']
            fn_args = call.get('args', {})
            
            print(f"--- AI suggests tool: {fn_name} ---")
            
            # STEP 2: Execute the actual Python function
            # getattr finds the function in tools.py by its string name
            tool_func = getattr(tools, fn_name)
            db_result = tool_func(**fn_args)
            
            print(f"--- Database Result: {db_result} ---")
            
            # STEP 3: Send the result back so Gemini can talk to the user
            follow_up = {
                "contents": [
                    {"role": "user", "parts": [{"text": user_message}]},
                    {"role": "model", "parts": [part]},
                    {
                        "role": "function",
                        "parts": [{
                            "functionResponse": {
                                "name": fn_name,
                                "response": {"result": db_result}
                            }
                        }]
                    }
                ],
                "tools": [{"function_declarations": TOOLS_DECLARATION}]
            }
            
            final_res = requests.post(URL, json=follow_up).json()
            answer = final_res['candidates'][0]['content']['parts'][0]['text']
            print(f"[Agent]: {answer}")
            
        else:
            print(f"[Agent]: {part.get('text', 'No text response')}")
            
    except Exception as e:
        print(f"Error: {e}\nResponse was: {json.dumps(response, indent=2)}")

if __name__ == "__main__":
    # Passing the phone number in the prompt helps the AI use the right tools immediately
    run_agent_turn("User Phone: +2348000000000. Message: Ndewo, do you have a brown canvas")