import streamlit as st
import requests
import json
import io
import random
import zipfile
from urllib.parse import quote
from PIL import Image
import base64
from shared.ui import page_header, inject_css, section_title, GOLD
from shared.ai_client import ask_ai, ask_ai_with_image, generate_image

st.set_page_config(page_title="Render Engine AI", layout="wide", page_icon="🎨")
inject_css()
page_header("🎨", "Render Engine AI", "Professional Photorealistic Visualization Studio")

ROOM_TYPES = ["Living Room", "Bedroom", "Kitchen", "Dining Room", "Bathroom", "Children's Room", "Pooja Room", "Entrance/Foyer", "Study/Home Office", "Outdoor Terrace", "Corridor", "Guest Room"]
DESIGN_STYLES = ["Modern Minimalist", "Scandinavian/Japandi", "Warm Contemporary", "Traditional Indian", "South Indian Traditional", "Rajasthani/Haveli", "Industrial Chic", "Bohemian/Eclectic", "Art Deco", "Mediterranean", "Arabic Majlis", "Biophilic/Nature", "Luxury Modern", "Mid-Century Modern", "Transitional"]
COLOR_PALETTES = ["Warm Neutrals (Beige, Cream, Taupe)", "Monochrome (Black, White, Grey)", "Earthy Tones (Terracotta, Olive, Ochre)", "Jewel Tones (Emerald, Sapphire, Ruby)", "Pastel Dream", "Dark & Moody", "Coastal Breezy", "Desert Sand", "High Contrast", "Soft Minimal"]
LIGHTING_MOODS = ["Bright & Airy Morning Light", "Warm Golden Hour Sunlight", "Cozy Evening with Warm Lamps", "Moody & Dramatic Spotlighting", "Soft Diffused Cloudy Day", "Cinematic", "Candlelight Glow", "Bright Studio Lighting"]
CAMERA_ANGLES = ["Wide Hero Shot (Full Room)", "Eye-Level Perspective", "Low Angle (Heroic Furniture)", "High Angle (Layout View)", "Close-up Material Detail", "Symmetrical One-Point Perspective", "Looking through Doorway"]
MATERIALS = ["Teak Wood", "White Oak", "Walnut", "Marble White", "Marble Black", "Rattan/Cane", "Velvet", "Linen", "Brass/Gold Metal", "Terracotta", "Ceramic", "Glass", "Leather", "Jute", "Bamboo", "Stone/Slate", "Mirror", "Fluted Glass", "Ribbed Wood Panels", "Exposed Brick", "Concrete", "Terrazzo", "Boucle Fabric", "Silk"]

def pollinations_render(prompt, width=1024, height=1024, seed=None):
    if prompt.startswith("Error:"):
        st.error(f"AI Error: Could not generate rendering prompt due to a network or API issue.\n\nDetails: {prompt}")
        return None
    
    # Transitioned to DALL-E 3 for "Pro" quality and to fix 404 errors with Pollinations
    try:
        size_str = f"{width}x{height}"
        # DALL-E 3 only supports specific sizes, mapping to 1024x1024 for stability
        img_bytes = generate_image(prompt, size="1024x1024")
        if img_bytes:
            return img_bytes
        else:
            st.error("DALL-E 3 failed to generate the image. Please check your API key and billing.")
            return None
    except Exception as e:
        st.error(f"Render engine failed: {e}")
        return None

def add_to_history(render_bytes, prompt, mode, label, metadata=None):
    st.session_state.render_history.insert(0, {
        "bytes": render_bytes, "prompt": prompt, "mode": mode,
        "label": label, "metadata": metadata or {}, "id": random.randint(10000, 99999)
    })
    if len(st.session_state.render_history) > 20:
        st.session_state.render_history = st.session_state.render_history[:20]

# Initialize Session State
if 'render_history' not in st.session_state: st.session_state.render_history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = ""
if 'active_mode' not in st.session_state: st.session_state.active_mode = "text_to_render"
if 'uploaded_design' not in st.session_state: st.session_state.uploaded_design = None
if 'reference_style_img' not in st.session_state: st.session_state.reference_style_img = None

with st.expander("⚙️ Global Render Output Settings"):
    col_w, col_h, col_v, col_i = st.columns(4)
    with col_w:
        render_width = st.select_slider("Width", options=[512, 640, 768, 1024, 1280], value=768)
    with col_h:
        render_height = st.select_slider("Height", options=[512, 640, 768, 1024], value=512)
    with col_v:
        vastu_mode = st.toggle("🕉️ Vastu-aware render", value=False)
    with col_i:
        intern_mode = st.toggle("🎓 Intern learning mode", value=False)

# Mode Selector
st.markdown("---")
cols = st.columns(6)
modes = [
    ("text_to_render", "✏️ Text to Render"),
    ("image_to_render", "🖼️ Design to Render"),
    ("style_transfer", "🔀 Style Transfer"),
    ("variations", "🎲 4 Variations"),
    ("material_swap", "🧱 Material Swap"),
    ("presentation", "📊 Client Pack")
]

for i, (m_id, m_label) in enumerate(modes):
    if cols[i].button(m_label, type="primary" if st.session_state.active_mode == m_id else "secondary", use_container_width=True):
        st.session_state.active_mode = m_id
        st.rerun()

st.markdown("---")

# ================================
# MODE 1: TEXT TO RENDER
# ================================
if st.session_state.active_mode == "text_to_render":
    st.subheader("✏️ Text to Render Generator")
    c1, c2 = st.columns(2)
    with c1:
        rt = st.selectbox("Room Type", ROOM_TYPES)
        ds = st.selectbox("Design Style", DESIGN_STYLES)
        mats = st.multiselect("Core Materials (Max 4)", MATERIALS, max_selections=4)
    with c2:
        cp = st.selectbox("Color Palette", COLOR_PALETTES)
        lm = st.selectbox("Lighting Mood", LIGHTING_MOODS)
        ca = st.selectbox("Camera Angle", CAMERA_ANGLES)
        
    special = st.text_input("Special Elements (e.g., 'Large chandelier, indoor swing')")
    notes = st.text_area("Designer Notes (Context for AI)")
    
    if st.button("Generate Optimized Render", type="primary", use_container_width=True):
        with st.spinner("🧠 AI Engineer crafting prompt & styling details..."):
            vastu_txt = "Show Vastu-correct furniture positions: seating on West/South wall facing East, NE corner open and light, SW has heavy furniture, plants in NE or N." if vastu_mode else ""
            sys = ("You are an elite interior design prompt engineer with a profoundly deep understanding of human psychology, "
                   "global design trends, and photorealistic AI rendering. You craft prompts that capture the soul of the space.")
            prompt = f"""
            Create a Stable Diffusion prompt for:
            Room: {rt}, Style: {ds}, Materials: {mats}, Colors: {cp}, Lighting: {lm}, Camera: {ca}, Special: {special}, Notes: {notes}
            {vastu_txt}
            Write ONLY the prompt starting with 'photorealistic interior design render,' ending with '8K ultra-detailed, architectural photography, Canon EOS R5, architectural digest style, award-winning interior design'. Maximum 220 words.
            """
            final_prompt = ask_ai(prompt, system=sys)
            st.session_state.current_prompt = final_prompt
            
        with st.spinner("🎨 Rendering photorealistic image..."):
            img_bytes = pollinations_render(final_prompt, width=render_width, height=render_height)
            if img_bytes:
                add_to_history(img_bytes, final_prompt, "text_to_render", f"{rt} - {ds}")
                st.image(img_bytes, use_container_width=True, caption="Final Output")
                
                c_d, c_r, c_v = st.columns(3)
                c_d.download_button("💾 Download High-Res", data=img_bytes, file_name="render.png", mime="image/png", use_container_width=True)
                if c_r.button("🔄 Regenerate (New Seed)", use_container_width=True): st.rerun()
                if c_v.button("🎲 Send to Variations", use_container_width=True): 
                    st.session_state.active_mode = "variations"
                    st.rerun()
                
                if intern_mode:
                    with st.spinner("🎓 Generating Intern Explanations..."):
                        ex = ask_ai(f"Explain why these design choices work well together in 5 bullet points for an interior design intern: Room: {rt}, Style: {ds}, Mats: {mats}, Colors: {cp}.")
                        st.info(f"**Intern Learning Note:**\n{ex}")

# ================================
# MODE 2: IMAGE TO RENDER
# ================================
elif st.session_state.active_mode == "image_to_render":
    st.subheader("🖼️ Design to Render (Sketch/CAD to Photoreal)")
    c1, c2 = st.columns(2)
    with c1:
        upload = st.file_uploader("Upload Design (Sketch/CAD/Concept)", type=['jpg', 'jpeg', 'png', 'webp'])
        if upload: st.session_state.uploaded_design = upload.getvalue()
        if st.session_state.uploaded_design:
            st.image(st.session_state.uploaded_design, caption="Your Input Design", use_container_width=True)
    
    with c2:
        user_inst = st.text_area("Additional specific instructions", placeholder="e.g., 'Do not change anything from the input, just make it photorealistic. Floor should be white marble.'")
        
        if st.session_state.uploaded_design and st.button("Convert Design to Render", type="primary", use_container_width=True):
            with st.spinner("👁️ AI Vision performing deep scan of layout and structural lines..."):
                sys = "You are an elite architectural analyst with pixel-perfect spatial precision."
                eval_p = """
                Deeply analyze this interior design image. This is a reference layout that MUST BE PRESERVED 100% in geometry.
                Extract: 
                1) Room type 
                2) EXACT Layout description — Provide coordinates or relative positions for walls, windows, doors, and furniture.
                3) Structural details — moldings, paneling on walls, specific ceiling features.
                4) Furniture — The exact type and placement of every item (sofa, TV, table, etc.).
                5) Lighting source — Location of windows and artificial lights.
                Return JSON format only with keys: room_type, spatial_geometry, wall_features, furniture_layout, lighting_points, designer_meta. 
                Focus on the structural 'skeleton' of the design. No markdown wrappers.
                """
                analysis_raw = ask_ai_with_image(eval_p, st.session_state.uploaded_design)
                
            with st.spinner("🧠 Engineering high-fidelity photorealistic prompt... (Marble Floor priority)"):
                prompt2 = f"""
                BASED ON THIS ARCHITECTURAL ANALYSIS: {analysis_raw}
                INSTRUCTIONS: {user_inst}
                
                MANDATORY RULE: PRESERVE THE EXACT SPATIAL LAYOUT AND GEOMETRY SHOWN IN THE ANALYSIS. DO NOT MOVE WALLS, WINDOWS, OR FURNITURE.
                
                Create a photorealistic render prompt that:
                1. REPLICATES the layout from the analysis with 100% precision.
                2. If the user instructions mention 'Marble floor', ensure it is described as premium, high-gloss marble.
                3. Upgrades all surfaces to photorealistic textures (8k resolution).
                4. Matches the exact wall paneling and structural details from the input.
                
                Start with 'photorealistic interior design render,' end with '8K ultra-detailed, professional architectural photography, architectural digest style, premium quality finish'.
                Write ONLY the prompt. Maximum 250 words.
                """
                final_prompt = ask_ai(prompt2, system="You are the ultimate high-fidelity staging AI. Your job is to RENDER the existing design, not RE-DESIGN it.")
                
            with st.spinner("🎨 Rendering..."):
                img_bytes = pollinations_render(final_prompt, width=render_width, height=render_height)
                if img_bytes:
                    add_to_history(img_bytes, final_prompt, "image_to_render", "Sketch to Render")
                    st.markdown("---")
                    r1, r2 = st.columns(2)
                    r1.markdown("**YOUR DESIGN INPUT**")
                    r1.image(st.session_state.uploaded_design, use_container_width=True)
                    r2.markdown("**PHOTOREALISTIC RENDER OUTPUT**")
                    r2.image(img_bytes, use_container_width=True)
                    
                    with st.expander("🔍 What AI detected in your design"):
                        try:
                            st.json(json.loads(analysis_raw))
                        except:
                            st.write(analysis_raw)
                            
                    if intern_mode:
                        with st.spinner("🎓 Generating Intern Explanations..."):
                            ex = ask_ai(f"Explain how AI interpreted the sketch and what was upgraded: {analysis_raw}")
                            st.info(f"**Intern Learning Note:**\n{ex}")
                            
                    st.download_button("💾 Download Render", data=img_bytes, file_name="ai_render.png", mime="image/png")

# ================================
# MODE 3: STYLE TRANSFER
# ================================
elif st.session_state.active_mode == "style_transfer":
    st.subheader("🔀 Style Transfer (Fuse style into your room)")
    c1, c2 = st.columns(2)
    with c1:
        ref_up = st.file_uploader("Reference Room (Style you want)", type=['jpg', 'jpeg', 'png', 'webp'], key="ref_up")
        if ref_up: st.session_state.reference_style_img = ref_up.getvalue()
        if st.session_state.reference_style_img: st.image(st.session_state.reference_style_img, caption="Reference Style")
    with c2:
        org_up = st.file_uploader("Your Room (To be transformed)", type=['jpg', 'jpeg', 'png', 'webp'], key="org_up")
        if org_up: st.session_state.uploaded_design = org_up.getvalue()
        if st.session_state.uploaded_design: st.image(st.session_state.uploaded_design, caption="Original Room")
        
    if st.session_state.reference_style_img and st.session_state.uploaded_design:
        if st.button("Transfer Style", type="primary", use_container_width=True):
            with st.spinner("👁️ Analyzing Reference Style..."):
                style_analysis = ask_ai_with_image("Describe ONLY the interior design style, materials, mood, lighting, and color palette of this image in dense keywords.", st.session_state.reference_style_img)
            with st.spinner("👁️ Analyzing Original Room Layout..."):
                room_analysis = ask_ai_with_image("Describe ONLY the structural layout, spatial volume, fixed elements (windows/doors), and primary furniture placement in this image.", st.session_state.uploaded_design)
            with st.spinner("🧠 Fusing concepts..."):
                prompt = f"""
                Create a Stable Diffusion prompt fusing these two inputs:
                Room Layout to preserve: {room_analysis}
                Style and Mood to apply: {style_analysis}
                Start with 'photorealistic interior design render,' end with '8K ultra-detailed, professional retouch'. Max 200 words.
                """
                final_prompt = ask_ai(prompt)
            with st.spinner("🎨 Rendering Transformed Room..."):
                img_bytes = pollinations_render(final_prompt, width=render_width, height=render_height)
                if img_bytes:
                    add_to_history(img_bytes, final_prompt, "style_transfer", "Style Transfer Result")
                    st.markdown("---")
                    colA, colB, colC = st.columns(3)
                    colA.image(st.session_state.reference_style_img, caption="Reference Style", use_container_width=True)
                    colB.image(st.session_state.uploaded_design, caption="Original Room", use_container_width=True)
                    colC.image(img_bytes, caption="Transferred Result", use_container_width=True)
                    st.download_button("💾 Download Result", data=img_bytes, file_name="style_transfer.png", mime="image/png")

# ================================
# MODE 4: 4 VARIATIONS
# ================================
elif st.session_state.active_mode == "variations":
    st.subheader("🎲 4 Variations Generator")
    c1, c2 = st.columns(2)
    with c1:
        rt = st.selectbox("Room Type", ROOM_TYPES, key="v_rt")
        ds = st.selectbox("Base Design Style", DESIGN_STYLES, key="v_ds")
    with c2:
        mats = st.multiselect("Core Materials", MATERIALS, key="v_mats", max_selections=3)
        cp = st.selectbox("Base Colors", COLOR_PALETTES, key="v_cp")
    
    notes = st.text_input("Design Notes / Instructions")
    var_type = st.selectbox("Variation Strategy", [
        "4 Lighting Moods (Morning/Evening/Night/Dramatic)",
        "4 Design Styles (keep same layout)",
        "4 Color Palettes (keep same style)",
        "4 Camera Angles (same render, different views)"
    ])
    
    if st.button("Generate 4 Variations", type="primary", use_container_width=True):
        st.info("Creating 4 distinct prompt variants. This will take ~30-40 seconds.")
        with st.spinner("🧠 Generating dynamic prompts..."):
            sys = "You are a master of varied iteratations in Stable Diffusion."
            pr = f"""
            I need 4 DIFFERENT photorealistic prompts for a {rt}. Base style: {ds}, Mats: {mats}, Colors: {cp}. Notes: {notes}.
            Strategy: {var_type}.
            Return ONLY a JSON array of 4 strings. No markdown formatting. Example: ["prompt1", "prompt2", "prompt3", "prompt4"]
            """
            res = ask_ai(pr, system=sys, expect_json=True)
            try:
                prompts = json.loads(res)
            except:
                st.error("Failed to parse variations.")
                prompts = []
                
        if len(prompts) == 4:
            results = []
            seeds = [1000, 1777, 2554, 3331]
            cols = st.columns(2)
            
            for idx, p in enumerate(prompts):
                with st.spinner(f"🎨 Rendering variation {idx+1}/4..."):
                    img_bytes = pollinations_render(p, width=render_width, height=render_height, seed=seeds[idx])
                    if img_bytes:
                        results.append(("V"+str(idx+1), img_bytes))
                        add_to_history(img_bytes, p, "variations", f"Var {idx+1}")
                        cols[idx % 2].image(img_bytes, caption=f"Variation {idx+1}", use_container_width=True)
                        cols[idx % 2].download_button(f"💾 Download Var {idx+1}", data=img_bytes, file_name=f"variation_{idx+1}.png", mime="image/png", key=f"dl_var_{idx}")
                        
            if len(results) == 4:
                # Create Zip
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w") as z:
                    for i, (name, b) in enumerate(results):
                        z.writestr(f"variation_{i+1}.png", b)
                buf.seek(0)
                st.download_button("📦 Download All as ZIP", data=buf, file_name="variations.zip", mime="application/zip", use_container_width=True)

# ================================
# MODE 5: MATERIAL SWAP
# ================================
elif st.session_state.active_mode == "material_swap":
    st.subheader("🧱 Material Swap Editor")
    if not st.session_state.render_history:
        st.warning("No render history found! Generate a render in Mode 1 first.")
        if st.button("Go to Text to Render"): 
            st.session_state.active_mode = "text_to_render"
            st.rerun()
    else:
        latest = st.session_state.render_history[0]
        c1, c2 = st.columns(2)
        c1.markdown("**Latest Render**")
        c1.image(latest['bytes'], use_container_width=True)
        
        with c2:
            st.markdown("**Swap Materials**")
            all_mats = MATERIALS + ["Painted white", "Painted grey", "Wallpaper", "Dark Oak", "Terrazzo Black", "Green Velvet"]
            old_mat = st.selectbox("Change this material", all_mats)
            new_mat = st.selectbox("Replace with", all_mats[::-1])
            ext = st.text_input("Optional additional tweaks")
            
            if st.button("Swap Material & Rerender", type="primary"):
                with st.spinner("🧠 Replacing materials in prompt..."):
                    p = f"""
                    Original prompt: {latest['prompt']}
                    I want to swap out '{old_mat}' and replace it entirely with '{new_mat}'. {ext}.
                    Return ONLY the new modified prompt. Keep all other layout and architecture perfectly identical so it feels like the exact same room, just with a new material.
                    """
                    new_p = ask_ai(p)
                with st.spinner("🎨 Rendering swap..."):
                    img_bytes = pollinations_render(new_p, width=render_width, height=render_height, seed=latest['metadata'].get('seed', random.randint(1000,9999)))
                    if img_bytes:
                        add_to_history(img_bytes, new_p, "material_swap", f"Swapped {old_mat} for {new_mat}")
                        st.markdown("---")
                        colA, colB = st.columns(2)
                        colA.image(latest['bytes'], caption=f"Before ({old_mat})", use_container_width=True)
                        colB.image(img_bytes, caption=f"After ({new_mat})", use_container_width=True)

# ================================
# MODE 6: CLIENT PRESENTATION PACK
# ================================
elif st.session_state.active_mode == "presentation":
    st.subheader("📊 Client Presentation Pack Generator")
    c1, c2 = st.columns(2)
    with c1:
        cn = st.text_input("Client Name")
        rt = st.selectbox("Room", ROOM_TYPES, key="p_rt")
        b_desc = st.text_area("Base Design Description")
    with c2:
        budget = st.select_slider("Budget Level", ["Economy", "Standard", "Premium", "Ultra-Luxury"])
        opts = st.multiselect("Select 3 Styling Options", DESIGN_STYLES, max_selections=3)
        
    if st.button("Generate 3-Option Presentation", type="primary", use_container_width=True):
        if len(opts) != 3 or not cn:
            st.warning("Please provide client name and exactly 3 options.")
        else:
            from shared.ui import gold_card
            gold_card(f"<h2 style='text-align:center'>Design Presentation for {cn}</h2><p style='text-align:center'>{rt} | Budget: {budget}</p>")
            pack_results = []
            seeds = [2000, 3111, 4222]
            p_cols = st.columns(3)
            
            for i in range(3):
                with p_cols[i]:
                    with st.spinner(f"Rendering Option {i+1}..."):
                        st.markdown(f"**Option {i+1}: {opts[i]}**")
                        p = f"Photorealistic interior design render of {rt}. Base: {b_desc}. Style: {opts[i]}. Looks like {budget} quality finish. 8k resolution, architectural digest."
                        img = pollinations_render(p, width=512, height=768, seed=seeds[i])
                        if img:
                            st.image(img, use_container_width=True)
                            pack_results.append((opts[i], img))
                            add_to_history(img, p, "presentation", f"Opt {i+1}: {opts[i]}")
                            
                            c_data = ask_ai(f"Write a 2-sentence emotional client pitch, 3 highlight bullet points, and an estimated cost range in INR for this {budget} {rt} in {opts[i]} style.")
                            st.info(c_data)
                            st.download_button(f"💾 Download Option {i+1}", data=img, file_name=f"option_{i+1}.png", mime="image/png", key=f"dl_opt_{i}", use_container_width=True)
            
            if len(pack_results) == 3:
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w") as z:
                    for i, (name, b) in enumerate(pack_results):
                        z.writestr(f"option_{i+1}_{name.replace(' ', '_')}.png", b)
                buf.seek(0)
                st.download_button("📦 Download Complete Pack as ZIP", data=buf, file_name=f"{cn}_Presentation.zip", mime="application/zip", use_container_width=True, type="primary")

# ================================
# PRESETS AND HISTORY
# ================================
st.markdown("---")
section_title("QUICK PRESETS")
pc1, pc2, pc3 = st.columns(3)
pc4, pc5, pc6 = st.columns(3)

preset_map = {
    "Japandi Living Room": ("photorealistic interior design render of living room, japandi style, warm wood, low furniture, minimal decor, soft sunlight, highly detailed 8k", pc1),
    "South Indian Traditional": ("photorealistic interior design render, south indian traditional living room, teak wood swing oonjal, brass lamps, athangudi tiles, highly detailed 8k", pc2),
    "Luxury Master Bedroom": ("photorealistic interior design render, luxury master bedroom, velvet headboard, gold accents, dark moody lighting, highly detailed 8k", pc3),
    "Minimalist Kitchen": ("photorealistic interior design render, minimalist kitchen, matte black cabinets, white marble island, bright natural light, highly detailed 8k", pc4),
    "Rajasthani Haveli Dining": ("photorealistic interior design render, rajasthani haveli dining room, carved wood arches, vibrant colors, royal lighting, highly detailed 8k", pc5),
    "Biophilic Home Office": ("photorealistic interior design render, biophilic home office, abundant indoor plants, natural daylight, wood desk, highly detailed 8k", pc6)
}

for name, (pr, col) in preset_map.items():
    if col.button(name, use_container_width=True):
        with st.spinner(f"Render Preset: {name}..."):
            img = pollinations_render(pr, width=render_width, height=render_height)
            if img:
                add_to_history(img, pr, "preset", name)
                # Show in a container at top
                st.session_state.active_mode = "text_to_render"
                st.rerun()

if st.session_state.render_history:
    st.markdown("---")
    section_title(f"RENDER HISTORY ({len(st.session_state.render_history)} items)")
    show_count = st.slider("Show how many?", 1, 20, min(6, len(st.session_state.render_history)))
    
    if len(st.session_state.render_history) >= 2:
        with st.expander("⚖️ Compare Two Renders"):
            opts = {f"{r['label']} (ID: {r['id']})": r for r in st.session_state.render_history}
            c_sel1, c_sel2 = st.columns(2)
            sel1 = c_sel1.selectbox("Render 1", list(opts.keys()), index=0)
            sel2 = c_sel2.selectbox("Render 2", list(opts.keys()), index=1)
            
            c_i1, c_i2 = st.columns(2)
            c_i1.image(opts[sel1]['bytes'], use_container_width=True, caption=sel1)
            c_i2.image(opts[sel2]['bytes'], use_container_width=True, caption=sel2)

    h_cols = st.columns(3)
    for i in range(show_count):
        r = st.session_state.render_history[i]
        with h_cols[i % 3]:
            st.image(r['bytes'], use_container_width=True, caption=f"{r['mode']} - {r['label']}")
            st.download_button("Download", data=r['bytes'], file_name=f"history_{r['id']}.png", mime="image/png", key=f"hist_dl_{r['id']}")
            
    buf2 = io.BytesIO()
    with zipfile.ZipFile(buf2, "w") as z:
        for r in st.session_state.render_history:
            z.writestr(f"{r['label']}_{r['id']}.png", r['bytes'])
    buf2.seek(0)
    st.download_button("📦 Download ALL History as ZIP", data=buf2, file_name="all_renders.zip", mime="application/zip")
