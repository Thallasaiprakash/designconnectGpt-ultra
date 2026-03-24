import streamlit as st
from shared.gemini_client import ask_gemini, ask_gemini_with_image
from shared.openai_client import ask_chatgpt, ask_chatgpt_with_image

def ask_ai(prompt: str, system: str = None, expect_json: bool = False) -> str:
    choice = st.session_state.get('model_choice', "Gemini 2.5 Flash")
    
    if "ChatGPT" in choice:
        return ask_chatgpt(prompt, system=system, expect_json=expect_json)
    else:
        return ask_gemini(prompt, system=system, expect_json=expect_json)

def ask_ai_with_image(prompt: str, image_bytes: bytes, mime: str = "image/jpeg") -> str:
    choice = st.session_state.get('model_choice', "Gemini 2.5 Flash")
    
    if "ChatGPT" in choice:
        return ask_chatgpt_with_image(prompt, image_bytes, mime=mime)
    else:
        return ask_gemini_with_image(prompt, image_bytes, mime=mime)
