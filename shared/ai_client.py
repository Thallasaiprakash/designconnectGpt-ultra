import streamlit as st
from shared.openai_client import ask_chatgpt, ask_chatgpt_with_image

def ask_ai(prompt: str, system: str = None, expect_json: bool = False) -> str:
    # Permanently using OpenAI as per user request
    return ask_chatgpt(prompt, system=system, expect_json=expect_json)

def ask_ai_with_image(prompt: str, image_bytes: bytes, mime: str = "image/jpeg") -> str:
    # Permanently using OpenAI as per user request
    return ask_chatgpt_with_image(prompt, image_bytes, mime=mime)
