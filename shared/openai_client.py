import openai
import os, json, re, time
import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

# Attempt to get API key from environment or streamlit secrets
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        api_key = None

if api_key:
    client = openai.OpenAI(api_key=api_key)
else:
    client = None

def ask_chatgpt(prompt: str, system: str = None, model: str = "gpt-4o", expect_json: bool = False) -> str:
    if not client:
        error_msg = "Error: OPENAI_API_KEY not found. Please set it in .env or Streamlit Secrets."
        return json.dumps({"error": error_msg}) if expect_json else error_msg
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"} if expect_json else None
            )
            
            content = response.choices[0].message.content.strip()
            
            if expect_json:
                # Basic validation/cleanup if needed
                match = re.search(r'\{.*\}|\[.*\]', content, re.DOTALL)
                if match:
                    return match.group(0)
                return content
                
            return content
        except Exception as e:
            err_str = str(e).lower()
            if "rate_limit" in err_str and attempt < 2:
                time.sleep(2)
                continue
            
            # Specific handling for auth/key errors
            if "401" in err_str or "auth" in err_str:
                error_msg = "Error: Invalid OpenAI API Key. Please check your .env or Streamlit Secrets."
            elif "400" in err_str or "expired" in err_str or "billing" in err_str:
                error_msg = "Error: OpenAI API Key expired, limit reached, or billing issue. Please renew your OpenAI subscription."
            else:
                error_msg = f"Error: {e}"
                
            return json.dumps({"error": error_msg}) if expect_json else error_msg

def ask_chatgpt_with_image(prompt: str, image_bytes: bytes, model: str = "gpt-4o", mime: str = "image/jpeg") -> str:
    if not client:
        return "Error: OPENAI_API_KEY not found. Please set it in .env or Streamlit Secrets."
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime};base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            err_str = str(e).lower()
            if "rate_limit" in err_str and attempt < 2:
                time.sleep(2)
                continue
            
            if "401" in err_str or "auth" in err_str:
                return "Error: Invalid OpenAI API Key."
            elif "400" in err_str or "expired" in err_str or "billing" in err_str:
                return "Error: OpenAI API Key expired or billing issue. Please renew."
            return f"Error: {e}"
