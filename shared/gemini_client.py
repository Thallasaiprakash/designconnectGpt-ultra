import google.generativeai as genai
import os, json, re
from dotenv import load_dotenv
load_dotenv(override=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
import re
from PIL import Image
import io
import time

def ask_gemini(prompt: str, system: str = None, expect_json: bool = False) -> str:
    for attempt in range(3):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system)
            response = model.generate_content(prompt)
            
            if expect_json:
                match = re.search(r'\{.*\}|\[.*\]', response.text, re.DOTALL)
                if match:
                    return match.group(0)
                else:
                    return json.dumps({"error": "No JSON found in response"})
                    
            return response.text.strip()
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                time.sleep(2)
                continue
            return json.dumps({"error": str(e)}) if expect_json else f"Error: {e}"

def ask_gemini_with_image(prompt: str, image_bytes: bytes, mime: str = "image/jpeg") -> str:
    print("ask_gemini_with_image CALLED")
    for attempt in range(3):
        try:
            print("Initializing model...")
            model = genai.GenerativeModel('gemini-2.5-flash')
            if "pdf" in mime:
                file_part = {"mime_type": "application/pdf", "data": image_bytes}
            else:
                print("Opening image...")
                file_part = Image.open(io.BytesIO(image_bytes))
                
            print("Generating content...")
            response = model.generate_content([prompt, file_part])
            print("Content generated successfully!")
            return response.text.strip()
        except Exception as e:
            print(f"Exception caught in ask_gemini_with_image: {e}")
            if "429" in str(e) and attempt < 2:
                time.sleep(2)
                continue
            return f"Error: {e}"
