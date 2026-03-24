import streamlit as st
import json
from shared.ui import page_header, inject_css, section_title, GOLD
from shared.ai_client import ask_ai

st.set_page_config(page_title="Lighting Intelligence", layout="wide", page_icon="💡")
inject_css()
page_header("💡", "Lighting Intelligence", "Professional illumination algorithms & scene planning")

if 'light_plan' not in st.session_state:
    st.session_state.light_plan = None

section_title("1. SPATIAL & MOOD PARAMETERS")
c1, c2, c3 = st.columns(3)
with c1:
    room_type = st.selectbox("Room Type", ["Living Room", "Master Bedroom", "Kitchen", "Dining Room", "Bathroom", "Study/Home Office", "Home Theater", "Corridor", "Retail Space", "Restaurant"])
    length = st.number_input("Length (feet)", min_value=5, max_value=100, value=16)
    width = st.number_input("Width (feet)", min_value=5, max_value=100, value=12)
with c2:
    ceiling_height = st.number_input("Ceiling Height (feet)", min_value=8, max_value=20, value=10)
    ceiling_type = st.selectbox("Ceiling Type", ["Flat", "POP False Ceiling with Cove", "Gypsum", "Coffered", "Wooden Panel", "Open"])
    natural_light = st.select_slider("Natural Light Available", ["Very Low", "Low", "Medium", "High", "Very High"], value="Medium")
with c3:
    mood = st.selectbox("Desired Lighting Mood", ["Bright & Energetic", "Warm & Cozy", "Dramatic & Moody", "Clean & Clinical", "Romantic", "Cinematic", "Focus/Productivity", "Biophilic/Natural"])
    activities = st.multiselect("Primary Activities", ["Relaxing", "Reading", "Cooking", "Dining", "Entertaining", "Working/Studying", "Exercising", "Sleeping", "Grooming"])
    vastu_light = st.toggle("🕉️ Vastu Compliance for Light & Energy", value=True)

st.markdown("---")
if st.button("Generate Lighting Masterplan", type="primary", use_container_width=True):
    with st.spinner("💡 Illuminating calculations underway... Analyzing lux levels & CCT..."):
        prompt = f"""
        Act as a Master Lighting Designer and Electrical Engineer.
        Design a complete lighting plan for:
        - Room: {room_type} ({length}x{width} ft, {ceiling_height}ft height, {ceiling_type})
        - Natural Light: {natural_light}
        - Mood: {mood}
        - Activities: {activities}
        - Vastu Required: {vastu_light}
        
        Use REALISTIC Indian product brands (Philips, Havells, Wipro, Crompton) and realistic current market pricing in INR.
        Return ONLY valid JSON:
        {{
          "lighting_concept": "2 sentences explaining the atmosphere",
          "total_fixtures": 10, "estimated_wattage": 150, "recommended_lux": 300, "lux_explanation": "brief reason",
          "fixtures": [
            {{"fixture_type": "name", "purpose": "ambient/task/accent", "quantity": 4, "wattage_each": 15, "cct_kelvin": 3000, "cct_description": "Warm White", "lumen_output": 1200, "placement": "where to place", "switch_group": 1, "dimmer_recommended": true, "product_suggestion": "brand & model", "approx_cost_inr": 800}}
          ],
          "switch_groups": [{{"group": 1, "controls": "all downlights", "use_case": "general illumination"}}],
          "dimmer_recommendations": "string advice on dimmer tech",
          "vastu_notes": "shastra rules applied (if enabled)",
          "energy_saving_tips": ["tip1", "tip2", "tip3"],
          "estimated_monthly_electricity": "cost breakdown based on 5 hours/day usage",
          "scene_presets": [{{"scene": "Movie Night", "settings": "dim group 1, group 2 off, cove 10%"}}],
          "total_fixture_cost_estimate": 10000, 
          "installation_cost_estimate": 3000
        }}
        """
        raw_res = ask_ai(prompt, expect_json=True)
        try:
            import re
            match = re.search(r'\{.*\}', raw_res, re.DOTALL)
            if match:
                st.session_state.light_plan = json.loads(match.group(0))
            else:
                st.session_state.light_plan = json.loads(raw_res)
        except Exception as e:
            st.error("AI Error: Failed to parse lighting data.")
            st.session_state.light_plan = None

if st.session_state.light_plan:
    data = st.session_state.light_plan
    section_title("2. LIGHTING MASTERPLAN")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Fixtures", data.get("total_fixtures", 0))
    m2.metric("Total Wattage", f"{data.get('estimated_wattage', 0)} W")
    m3.metric("Target Brightness", f"{data.get('recommended_lux', 0)} LUX", data.get("lux_explanation", ""))
    m4.metric("Est. Monthly Elec.", data.get("estimated_monthly_electricity", "0 INR").split(' ')[0] + " INR")
    
    st.markdown(f"<div style='border:1px solid {GOLD}; padding:15px; border-radius:10px; background-color:#1a1c24;'><b>💡 Concept:</b><br/>{data.get('lighting_concept', '')}</div><br/>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("🔦 Detailed Fixture Schedule")
        for f in data.get('fixtures', []):
            with st.expander(f"{f.get('quantity')}x {f.get('fixture_type')} ({f.get('cct_kelvin')}K)"):
                st.write(f"**Purpose:** {f.get('purpose')} | **Placement:** {f.get('placement')}")
                st.write(f"**Specs:** {f.get('wattage_each')}W each | {f.get('lumen_output')} Lumens | Dimmer: {'Yes' if f.get('dimmer_recommended') else 'No'} | Switch Group {f.get('switch_group')}")
                st.write(f"**Product Suggestion:** {f.get('product_suggestion')} (₹{f.get('approx_cost_inr', 0)} each)")
    
    with col_b:
        st.subheader("🎛️ Control Architecture")
        for s in data.get('switch_groups', []):
            st.markdown(f"<div style='border-left: 3px solid {GOLD}; padding-left: 10px; margin-bottom: 10px;'><b>Group {s.get('group')}</b>: {s.get('controls')}<br/><small>{s.get('use_case')}</small></div>", unsafe_allow_html=True)
        st.write(f"**Dimmer Note:** {data.get('dimmer_recommendations', '')}")
        
    st.markdown("---")
    st.subheader("🎭 Smart Scene Presets")
    scenes = data.get("scene_presets", [])
    s_cols = st.columns(min(3, max(1, len(scenes))))
    for idx, sc in enumerate(scenes):
        s_cols[idx % len(s_cols)].info(f"**{sc.get('scene')}**\n\n{sc.get('settings')}")
        
    st.markdown("---")
    c_l, c_r = st.columns(2)
    with c_l:
        st.subheader("💰 Cost Summary")
        st.write(f"**Fixtures Estimate:** ₹ {data.get('total_fixture_cost_estimate', 0):,.2f}")
        st.write(f"**Installation Estimate:** ₹ {data.get('installation_cost_estimate', 0):,.2f}")
        total = data.get('total_fixture_cost_estimate', 0) + data.get('installation_cost_estimate', 0)
        st.markdown(f"<h3 style='color:{GOLD}'>Grand Total: ₹ {total:,.2f}</h3>", unsafe_allow_html=True)
    with c_r:
        if vastu_light and data.get('vastu_notes'):
            st.success(f"**🕉️ Vastu Compliance:** {data.get('vastu_notes')}")
        st.info("**🌱 Energy Savings:**\n" + "\n".join([f"- {t}" for t in data.get('energy_saving_tips', [])]))
        
    # Download plan
    plan_txt = json.dumps(data, indent=2)
    st.download_button("💾 Download Lighting Schedule (JSON)", data=plan_txt, file_name="lighting_plan.json", mime="application/json")
