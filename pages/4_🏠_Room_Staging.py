import streamlit as st
import requests
import json
import io
import random
from urllib.parse import quote
from shared.ui import page_header, inject_css, section_title, GOLD
from shared.ai_client import ask_ai, ask_ai_with_image

st.set_page_config(page_title="Room Staging AI", layout="wide", page_icon="🏠")
inject_css()
page_header("🏠", "Room Staging AI", "Transform Empty or Outdated Rooms instantly.")

# Define Constants
DESIGN_STYLES = ["Modern Minimalist", "Scandinavian", "Japandi", "Warm Contemporary", "Traditional Indian", "Industrial Chic", "Bohemian", "Art Deco", "Coastal", "Farmhouse", "Mid-Century Modern", "Transitional", "Luxury Modern", "Eclectic", "South Indian Traditional"]
COLOR_SCHEMES = ["Warm Neutrals", "Monochrome", "Earthy Tones", "Jewel Tones", "Pastel Dream", "Dark & Moody", "Bright & Vibrant", "Soft Minimal"]
KEEP_OPTIONS = ["Window positions", "Room size/shape", "Flooring type", "Main walls", "Ceiling height", "Current Lighting Layout"]
BUDGET_LEVELS = ["Budget Friendly", "Mid Range", "Premium", "Luxury"]

def safe_pollinations_render(prompt, width=768, height=512):
    if prompt.startswith("Error:"):
        st.error(f"AI API Error: {prompt}")
        return None
    seed = random.randint(1000, 9999)
    encoded = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&seed={seed}&nologo=True&model=flux"
    try:
        res = requests.get(url, timeout=90)
        if res.status_code == 200:
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(res.content))
                img.load()
                return res.content
            except Exception:
                st.error("Render Engine returned invalid or corrupted image data. The server might be overloaded, please try again.")
                return None
        else:
            st.error(f"API Error (Render Engine): {res.status_code}")
            return None
    except Exception as e:
        st.error(f"Render network failed: {e}")
        return None

# Session State
if 'staging_original' not in st.session_state:
    st.session_state.staging_original = None
if 'staging_result' not in st.session_state:
    st.session_state.staging_result = None
if 'room_analysis' not in st.session_state:
    st.session_state.room_analysis = None
if 'last_description' not in st.session_state:
    st.session_state.last_description = None

# SECTION 1: UPLOAD & ANALYZE
section_title("1. UPLOAD ROOM PHOTO")
upload = st.file_uploader("Take a photo of the client's current room", type=["jpg", "jpeg", "png", "webp"])

if upload:
    # Check if a NEW file was uploaded (reset state if so)
    if st.session_state.staging_original != upload.getvalue():
        st.session_state.staging_original = upload.getvalue()
        st.session_state.staging_result = None
        st.session_state.room_analysis = None
        st.session_state.last_description = None

if st.session_state.staging_original:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(st.session_state.staging_original, caption="Current Room", use_container_width=True)
    
    with c2:
        if not st.session_state.room_analysis:
            with st.spinner("👁️ AI Vision analyzing room structure and issues..."):
                prompt = """Analyze this interior room photo. Identify: 
                1) Room type 
                2) Current design style 
                3) Approximate size (small/medium/large) 
                4) Design issues from a professional perspective (clutter, poor lighting, outdated, empty, etc.)
                5) Materials currently visible. 
                Return strictly JSON: {"room_type": "...", "current_style": "...", "size": "...", "issues": "...", "materials": "..."}"""
                raw_json = ask_ai_with_image(prompt, st.session_state.staging_original)
                
                try:
                    import re
                    match = re.search(r'\{.*\}', raw_json, re.DOTALL)
                    if match:
                        st.session_state.room_analysis = json.loads(match.group(0))
                    else:
                        st.session_state.room_analysis = json.loads(raw_json)
                except:
                    st.error("Failed to parse structural analysis. Proceeding with manual input instead.")
                    st.session_state.room_analysis = {"room_type": "Unknown", "current_style": "Unknown", "size": "Unknown", "issues": "Unknown", "materials": "Unknown"}
        
        if st.session_state.room_analysis:
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("Detected Room", st.session_state.room_analysis.get("room_type", "N/A"))
            c_m2.metric("Current Style", st.session_state.room_analysis.get("current_style", "N/A"))
            c_m3.metric("Room Size", st.session_state.room_analysis.get("size", "N/A"))
            
            issues = st.session_state.room_analysis.get("issues", "")
            if issues and issues.lower() not in ["none", "n/a", "unknown"]:
                st.warning(f"**Identified Issues to fix:** {issues}")
                
            st.info(f"**Current Materials:** {st.session_state.room_analysis.get('materials', 'N/A')}")

st.markdown("---")

# SECTION 2: CHOOSE REDESIGN
if st.session_state.staging_original:
    section_title("2. REDESIGN STRATEGY")
    sc1, sc2 = st.columns(2)
    with sc1:
        new_style = st.selectbox("New Design Style", DESIGN_STYLES, index=2)
        color_scheme = st.selectbox("Color Palette", COLOR_SCHEMES)
    with sc2:
        keep_elements = st.multiselect("Keep from original (preserve geometry)", KEEP_OPTIONS, default=["Window positions", "Room size/shape"])
        budget_level = st.select_slider("Target Finish & Quality", BUDGET_LEVELS, value="Premium")
        
    if st.button("Generate Staged Design", type="primary", use_container_width=True):
        st.session_state.current_style_selection = f"{new_style} - {color_scheme}"
        rt = st.session_state.room_analysis.get("room_type", "room") if st.session_state.room_analysis else "room"
        
        # We need to construct a highly optimized prompt
        with st.spinner(f"🧠 Prompt Engineering {new_style} staging..."):
            render_prompt = f"photorealistic interior design render, {new_style} style {rt}, {color_scheme} color palette, {budget_level} interior, professionally staged, beautifully furnished, warm natural lighting, 8K ultra-detailed, architectural photography, award winning design, no people, highly detailed textures."
            
            st.session_state.current_prompt_used = render_prompt
            
        with st.spinner(f"🎨 Rendering {rt}..."):
            img_out = safe_pollinations_render(render_prompt)
            if img_out:
                st.session_state.staging_result = img_out
                # Automatically generate pitch description
                with st.spinner("✍️ Writing professional pitch..."):
                    pitch_prompt = f"Write a 3-sentence professional interior design description of this newly staged {new_style} {rt} featuring a {color_scheme} palette built for a {budget_level} budget. Make it sell the dream to a client. No marketing fluff, just elegant design talk."
                    st.session_state.last_description = ask_ai(pitch_prompt)

st.markdown("---")

# SECTION 4: BEFORE/AFTER
if st.session_state.staging_result:
    section_title("3. STAGING RESULTS")
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("**BEFORE — Original Room**")
        st.image(st.session_state.staging_original, use_container_width=True)
    with bc2:
        style_label = getattr(st.session_state, 'current_style_selection', 'Redesign')
        st.markdown(f"**<span style='color:{GOLD}; font-size:18px;'>AFTER — {style_label}</span>**", unsafe_allow_html=True)
        st.image(st.session_state.staging_result, use_container_width=True)
        
    if st.session_state.last_description:
        st.markdown(f"<div style='border:1px solid {GOLD}; padding:15px; border-radius:10px; background-color:#1a1c24;'><b>✨ Professional Pitch:</b><br/>{st.session_state.last_description}</div>", unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        
    cmd1, cmd2, cmd3 = st.columns(3)
    cmd1.download_button("💾 Download Render", data=st.session_state.staging_result, file_name="staged_room.png", mime="image/png", use_container_width=True)
    
    if cmd2.button("🔄 Regenerate (New Seed)", use_container_width=True):
        with st.spinner("🎨 Re-rendering..."):
            new_img = safe_pollinations_render(st.session_state.current_prompt_used)
            if new_img:
                st.session_state.staging_result = new_img
                st.rerun()
                
    if cmd3.button("🗑️ Try Different Style", use_container_width=True):
        st.session_state.staging_result = None
        st.session_state.last_description = None
        st.rerun()
