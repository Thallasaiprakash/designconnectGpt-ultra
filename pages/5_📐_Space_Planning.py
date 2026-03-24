import streamlit as st
import json
import re
from shared.ui import page_header, inject_css, section_title, GOLD
from shared.ai_client import ask_ai

st.set_page_config(page_title="Space Planning Assistant", layout="wide", page_icon="📐")
inject_css()
page_header("📐", "Space Planning Assistant", "Intelligent Layouts & Spatial Organization")

if 'space_plan' not in st.session_state:
    st.session_state.space_plan = None

ROOM_TYPES = ["Living Room", "Bedroom", "Master Bedroom", "Kitchen", "Dining Room", "Bathroom", "Study/Home Office", "Children's Room", "Guest Room", "Pooja Room", "Home Theater", "Gym/Workout"]
DESIGN_STYLES = ["Modern Minimalist", "Scandinavian", "Japandi", "Traditional Indian", "Industrial Chic", "Bohemian", "Art Deco", "Mid-Century Modern", "Transitional", "Luxury Modern"]
FURNITURE_OPTS = ["Sofa 3-seater", "Sofa 2-seater", "Armchair", "Coffee Table", "TV Unit", "Dining Table", "Bed King", "Bed Queen", "Study Table", "Office Chair", "Wardrobe", "Bookshelf", "Console Table", "Side Table", "Plants/Planters", "Floor Lamp"]

section_title("1. ROOM DETAILS")
c1, c2, c3 = st.columns(3)
with c1:
    room_type = st.selectbox("Room Type", ROOM_TYPES)
    length = st.number_input("Length (feet)", min_value=6, max_value=60, value=16)
with c2:
    width = st.number_input("Width (feet)", min_value=6, max_value=60, value=12)
    ceiling = st.number_input("Ceiling Height (feet)", min_value=8, max_value=16, value=10)
with c3:
    door_pos = st.selectbox("Main Door Position", ["North Wall", "South Wall", "East Wall", "West Wall"])
    window_pos = st.multiselect("Window Positions", ["North Wall", "South Wall", "East Wall", "West Wall"])

section_title("2. REQUIREMENTS")
r1, r2 = st.columns(2)
with r1:
    family_size = st.slider("Typical Occupancy (People)", 1, 10, 3)
    style = st.selectbox("Design Style", DESIGN_STYLES)
with r2:
    must_have = st.multiselect("Must-have Furniture", FURNITURE_OPTS)
    avoid_items = st.multiselect("Items to Avoid", FURNITURE_OPTS)

vastu = st.toggle("🕉️ Vastu Compliance", value=True)
accessible = st.toggle("♿ Accessibility Friendly (Wheelchair clear paths)", value=False)

st.markdown("---")
if st.button("Generate Space Plan", type="primary", use_container_width=True):
    with st.spinner("📐 Architect AI is drafting space plans and checking Vastu alignments..."):
        prompt = f"""
        Act as an elite interior architect and space planner.
        Create a detailed spatial plan for this room:
        - Room: {room_type} ({length}x{width} ft, {ceiling}ft ceiling)
        - Entrances: Door on {door_pos}, Windows on {window_pos}
        - Occupancy: {family_size} people. Style: {style}
        - Include: {must_have}
        - Exclude: {avoid_items}
        - Vastu Required: {vastu}
        - Accessibility Required: {accessible}
        
        Return ONLY valid JSON matching this exact structure:
        {{
          "room_summary": "2 sentences describing the spatial strategy",
          "total_area_sqft": {length * width},
          "usable_area_sqft": "number plus unit",
          "circulation_clearances": "description of pathway sizes",
          "furniture_layout": [
            {{"item": "item name", "dimensions_ft": "LxW", "placement": "specific placement with wall name and distance", "vastu_reason": "if vastu enabled, explain here", "color_suggestion": "color"}}
          ],
          "zones": [{{"zone_name": "name", "zone_description": "desc", "location": "where"}}],
          "traffic_flow": "description",
          "lighting_zones": ["primary", "accent", "task"],
          "storage_solutions": ["idea 1", "idea 2", "idea 3"],
          "dos": ["do1", "do2", "do3", "do4"],
          "donts": ["dont1", "dont2", "dont3", "dont4"],
          "ascii_layout": "A creative ASCII art text diagram mapping the room walls, door, windows, and major furniture. Use standard keyboard characters."
        }}
        """
        
        raw_res = ask_ai(prompt, expect_json=True)
        if raw_res.startswith("Error:"):
            st.error(f"API Error during Space Planning analysis: {raw_res}")
            st.session_state.space_plan = None
        else:
            try:
                import re
                match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                if match:
                    st.session_state.space_plan = json.loads(match.group(0))
                else:
                    st.session_state.space_plan = json.loads(raw_res)
            except Exception as e:
                st.error("AI Error: Failed to parse spatial data JSON. Please try again.")
                st.session_state.space_plan = None

if st.session_state.space_plan:
    data = st.session_state.space_plan
    section_title("3. SPATIAL MASTERPLAN")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Area", f"{data.get('total_area_sqft', 0)} sqft")
    m2.metric("Usable Area", data.get('usable_area_sqft', 'N/A'))
    m3.metric("Furniture Items", len(data.get('furniture_layout', [])))
    
    st.markdown(f"<div style='border:1px solid {GOLD}; padding:15px; border-radius:10px; background-color:#1a1c24;'><b>📐 Strategy:</b><br/>{data.get('room_summary', '')}<br/><br/><b>🚶 Circulation:</b> {data.get('circulation_clearances', '')}<br/><b>🌊 Traffic Flow:</b> {data.get('traffic_flow', '')}</div><br/>", unsafe_allow_html=True)
    
    c_a, c_b = st.columns([1, 1])
    with c_a:
        st.subheader("🗺️ ASCII Floor Plan")
        st.code(data.get('ascii_layout', 'ASCII layout not available'), language='text')
    
    with c_b:
        st.subheader("🛋️ Furniture Layout Schedule")
        for f in data.get('furniture_layout', []):
            with st.expander(f"📌 {f.get('item')} ({f.get('dimensions_ft')})"):
                st.write(f"**Placement:** {f.get('placement')}")
                if vastu and f.get('vastu_reason'):
                    st.success(f"**🕉️ Vastu:** {f.get('vastu_reason')}")
                st.info(f"**🎨 Color Suggestion:** {f.get('color_suggestion')}")

    st.markdown("---")
    st.subheader("🧩 Functional Zones")
    z_cols = st.columns(len(data.get('zones', [1, 2, 3])))
    for idx, z in enumerate(data.get('zones', [])):
        with z_cols[idx % len(z_cols)]:
            st.markdown(f"<div style='border-left: 3px solid {GOLD}; padding-left: 10px; margin-bottom: 10px;'><b>{z.get('zone_name')}</b><br/>{z.get('location')}<br/><small>{z.get('zone_description')}</small></div>", unsafe_allow_html=True)
            
    st.markdown("---")
    l_col, s_col = st.columns(2)
    with l_col:
        st.subheader("💡 Lighting Zones")
        for lz in data.get('lighting_zones', []): st.write(f"- {lz}")
    with s_col:
        st.subheader("📦 Storage Solutions")
        for ss in data.get('storage_solutions', []): st.write(f"- {ss}")
        
    st.markdown("---")
    do_col, dont_col = st.columns(2)
    with do_col:
        st.subheader("✅ Spatial Do's")
        for d in data.get('dos', []): st.write(f"✔️ {d}")
    with dont_col:
        st.subheader("❌ Spatial Don'ts")
        for d in data.get('donts', []): st.write(f"🚫 {d}")
        
    # Download as text file
    plan_txt = json.dumps(data, indent=2)
    st.download_button("💾 Download Masterplan (JSON)", data=plan_txt, file_name="space_plan.json", mime="application/json")
