import openai
import os, json, re
from dotenv import load_dotenv
import time

load_dotenv(override=True)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_chatgpt(prompt: str, system: str = None, model: str = "gpt-4o", expect_json: bool = False) -> str:
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
            if "rate_limit" in str(e).lower() and attempt < 2:
                time.sleep(2)
                continue
            return json.dumps({"error": str(e)}) if expect_json else f"Error: {e}"

def ask_chatgpt_with_image(prompt: str, image_bytes: bytes, model: str = "gpt-4o", mime: str = "image/jpeg") -> str:
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
            if "rate_limit" in str(e).lower() and attempt < 2:
                time.sleep(2)
                continue
            return f"Error: {e}"
