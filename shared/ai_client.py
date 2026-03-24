from shared.openai_client import ask_chatgpt, ask_chatgpt_with_image, generate_dalle_image

def ask_ai(prompt: str, system: str = None, expect_json: bool = False) -> str:
    # Permanently using OpenAI as per user request
    return ask_chatgpt(prompt, system=system, expect_json=expect_json)

def ask_ai_with_image(prompt: str, image_bytes: bytes, mime: str = "image/jpeg") -> str:
    # Permanently using OpenAI as per user request
    return ask_chatgpt_with_image(prompt, image_bytes, mime=mime)

def generate_image(prompt: str, size: str = "1024x1024") -> bytes:
    # Using DALL-E 3 for professional rendering
    return generate_dalle_image(prompt, size=size)
