import streamlit as st
import json
import io
import ezdxf
from shared.ui import page_header, inject_css, section_title, GOLD
from shared.gemini_client import ask_gemini

st.set_page_config(page_title="CAD Drafting & DXF", layout="wide", page_icon="📋")
inject_css()
page_header("📋", "CAD Guidance & DXF Generator", "Drafting workflows, auto-generated base DXF floors & dimensional standards")

tab1, tab2, tab3 = st.tabs(["📐 AutoCAD Workflow Guide", "🏗️ DXF Base Generator", "📏 Standard Dimensions Reference"])

# ================================
# TAB 1: AUTOCAD WORKFLOW GUIDE
# ================================
with tab1:
    if 'cad_guide' not in st.session_state: st.session_state.cad_guide = None
    
    st.subheader("AutoCAD Step-by-Step AI Guide")
    c1, c2, c3 = st.columns(3)
    with c1:
        dwg_type = st.selectbox("Drawing Type", ["Floor Plan Full House", "Floor Plan Single Room", "Elevation Front", "Elevation Interior Wall", "Reflected Ceiling Plan", "Electrical Layout", "Furniture Layout"])
        scale = st.selectbox("Scale", ["1:50", "1:100", "1:200", "1:500", "1:10", "1:20"], index=1)
    with c2:
        l_mm = st.number_input("Plot Length (mm)", min_value=1000, max_value=50000, value=9144)
        w_mm = st.number_input("Plot Width (mm)", min_value=1000, max_value=50000, value=6096)
    with c3:
        software = st.selectbox("Software", ["AutoCAD 2024", "AutoCAD 2023", "AutoCAD LT", "BricsCAD", "DraftSight"])
        skill = st.select_slider("Skill Level", ["Complete Beginner", "Novice", "Intermediate", "Advanced"])
        
    inc_short = st.toggle("Include Keyboard Shortcuts", value=True)
    inc_mistakes = st.toggle("Include Common Mistakes to Avoid", value=True)

    if st.button("Generate Workflow Guide", type="primary", use_container_width=True):
        with st.spinner(f"🧠 AI CAD Master mapping out {software} {dwg_type} workflow..."):
            prompt = f"""
            Act as an Expert CAD Manager. Write a workflow guide for drafting a {dwg_type} in {software}.
            Plot: {l_mm}x{w_mm} mm. Scale: {scale}. User level: {skill}.
            Include shortcuts: {inc_short}. Include mistakes: {inc_mistakes}.
            Return JSON:
            {{
              "workflow_title": "string", "estimated_time": "string",
              "layer_structure": [{{"layer_name": "name", "color_num": 1, "linetype": "Continuous", "lineweight": 0.35, "purpose": ""}}],
              "setup_steps": [{{"step": 1, "title": "", "commands": "exact command line text", "shortcut": "", "tip": "", "common_mistake": ""}}],
              "drawing_steps": [{{"step": 1, "title": "", "command_sequence": "exact commands", "shortcut": "", "explanation": "", "common_mistake": ""}}],
              "text_settings": {{"style": "Arial", "height_mm": 2.5, "annotation_scale": "Yes"}},
              "dimension_settings": {{"overall_scale": 1, "text_height": 2.5, "arrow_size": 2.5}},
              "save_and_export": ["3 instructions"],
              "pro_tips": ["5 pro tips"],
              "reference_standards": ["IS codes"]
            }}
            """
            res = ask_gemini(prompt, expect_json=True)
            if res.startswith("Error:"):
                st.error(f"API Error during CAD guide generation: {res}\n\nPlease wait 60 seconds for the free tier limit to reset.")
                st.session_state.cad_guide = None
            else:
                try:
                    import re
                    match = re.search(r'\{.*\}', res, re.DOTALL)
                    if match:
                        st.session_state.cad_guide = json.loads(match.group(0))
                    else:
                        st.session_state.cad_guide = json.loads(res)
                except Exception as e:
                    st.error("JSON Parsing Error.")
                    st.session_state.cad_guide = None
                
    if st.session_state.cad_guide:
        data = st.session_state.cad_guide
        st.markdown(f"### {data.get('workflow_title')} (Est. Time: {data.get('estimated_time')})")
        
        st.markdown("#### 🎨 Recommended Layer Structure")
        Layer_cols = st.columns(3)
        for idx, layer in enumerate(data.get("layer_structure", [])):
            with Layer_cols[idx % 3]:
                st.markdown(f"**{layer.get('layer_name')}** (Color: {layer.get('color_num', 7)})<br/>LW: {layer.get('lineweight')} | LT: {layer.get('linetype')}<br/>_{layer.get('purpose')}_", unsafe_allow_html=True)
                
        st.markdown("---")
        st.markdown("#### ⚙️ Initial Setup Steps")
        for step in data.get("setup_steps", []):
            with st.expander(f"Step {step.get('step')}: {step.get('title')}"):
                st.code(step.get("commands", ""), language="bash")
                if step.get("shortcut"): st.info(f"Keyboard: `{step.get('shortcut')}`")
                if step.get("tip"): st.success(f"Tip: {step.get('tip')}")
                if step.get("common_mistake"): st.error(f"Avoid: {step.get('common_mistake')}")
                
        st.markdown("#### 🏗️ Core Drafting Sequence")
        for step in data.get("drawing_steps", []):
            with st.expander(f"Drafting Phase {step.get('step')}: {step.get('title')}"):
                st.code(step.get("command_sequence", ""), language="bash")
                st.write(f"**Explanation:** {step.get('explanation')}")
                if step.get("shortcut"): st.info(f"Keyboard: `{step.get('shortcut')}`")
                if step.get("common_mistake"): st.error(f"Avoid: {step.get('common_mistake')}")
                
        c_l, c_r = st.columns(2)
        with c_l:
            st.markdown("#### 📏 Text & Dim Settings")
            st.json({"Text": data.get("text_settings", {}), "Dimensions": data.get("dimension_settings", {})})
            st.markdown("#### 💾 Save & Export")
            for x in data.get("save_and_export", []): st.write(f"- {x}")
        with c_r:
            st.markdown("#### 💎 Professional Tips")
            for pt in data.get("pro_tips", []): st.write(f"- {pt}")
            st.markdown("#### 📚 Reference Codes")
            for code in data.get("reference_standards", []): st.write(f"- {code}")

        guide_json = json.dumps(data, indent=2)
        st.download_button("💾 Download Workflow Guide", data=guide_json, file_name="CAD_Workflow.json", mime="application/json")


# ================================
# TAB 2: DXF BASE GENERATOR
# ================================
with tab2:
    st.subheader("Automated .DXF Base File Generator")
    st.write("Generate a quick accurately-scaled barebones `.dxf` layout to jumpstart your drafting process.")
    
    d1, d2 = st.columns(2)
    with d1:
        p_len = st.number_input("Total Plot Length (mm)", 1000, 100000, 9000)
        p_wid = st.number_input("Total Plot Width (mm)", 1000, 100000, 6000)
        wall_thk = st.number_input("Exterior Wall Thickness (mm)", 100, 500, 230)
    with d2:
        rooms_inc = st.multiselect("Interior Rooms (Abstract Split)", ["Living Room", "Master Bedroom", "Kitchen", "Bathroom", "Corridor", "Balcony"], default=["Living Room", "Master Bedroom", "Kitchen"])
        add_dims = st.toggle("Include Dimensions", value=True)
        add_txt = st.toggle("Include Room Labels", value=True)
        
    if st.button("Generate Base .DXF File", type="primary"):
        with st.spinner("Drafting DXF Vector Data..."):
            try:
                doc = ezdxf.new("R2010")
                doc.header['$INSUNITS'] = 4 # millimeters
                
                doc.layers.add("PLOT_BOUNDARY", color=7, lineweight=50)
                doc.layers.add("WALLS", color=1, lineweight=35)
                doc.layers.add("DIMENSIONS", color=3, lineweight=18)
                doc.layers.add("TEXT", color=7, lineweight=18)
                doc.layers.add("ROOMS", color=2, lineweight=25)
                
                msp = doc.modelspace()
                
                # Plot outline
                msp.add_lwpolyline([(0,0), (p_len, 0), (p_len, p_wid), (0, p_wid), (0,0)], dxfattribs={'layer': 'PLOT_BOUNDARY'})
                # Inner wall
                iw_l, iw_w = p_len - (wall_thk*2), p_wid - (wall_thk*2)
                msp.add_lwpolyline([(wall_thk, wall_thk), (wall_thk+iw_l, wall_thk), (wall_thk+iw_l, wall_thk+iw_w), (wall_thk, wall_thk+iw_w), (wall_thk, wall_thk)], dxfattribs={'layer': 'WALLS'})
                
                # Abstract grid depending on rooms included
                num_rooms = len(rooms_inc)
                if num_rooms > 0:
                    span_x = iw_l / num_rooms
                    for i in range(1, num_rooms):
                        x_pos = wall_thk + (span_x * i)
                        msp.add_line((x_pos, wall_thk), (x_pos, wall_thk+iw_w), dxfattribs={'layer': 'WALLS'})
                
                if add_txt:
                    if num_rooms > 0:
                        span_x = iw_l / num_rooms
                        for i, r_name in enumerate(rooms_inc):
                            x_center = wall_thk + (span_x * i) + (span_x / 2)
                            y_center = wall_thk + (iw_w / 2)
                            msp.add_text(r_name, dxfattribs={'layer': 'TEXT', 'height': 200}).set_placement((x_center, y_center), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
                            
                if add_dims:
                    # Overall Dimension
                    dim = msp.add_linear_dim(base=(p_len/2, p_wid + 500), p1=(0, p_wid), p2=(p_len, p_wid), dxfattribs={'layer': 'DIMENSIONS'})
                    dim.render()
                    dim2 = msp.add_linear_dim(base=(-500, p_wid/2), p1=(0, 0), p2=(0, p_wid), angle=90, dxfattribs={'layer': 'DIMENSIONS'})
                    dim2.render()

                s_io = io.StringIO()
                doc.write(s_io)
                dxf_str = s_io.getvalue()
                
                st.success("DXF Generation Complete!")
                st.download_button("💾 Download Base.dxf", data=dxf_str, file_name="Base_Layout.dxf", mime="application/dxf", type="primary", use_container_width=True)
                
            except Exception as e:
                st.error(f"Failed to generate DXF: {e}")

# ================================
# TAB 3: STANDARD DIMENSIONS
# ================================
with tab3:
    st.subheader("Architectural Standards & Dimensions")
    st.write("Reference material for accurate drafting.")
    
    with st.expander("🚪 Door & Circulation Dimensions", expanded=True):
        st.markdown(f"**Main Entrance:** <span style='color:{GOLD}'>900 x 2100 mm</span> (Min) to 1200 x 2400 mm", unsafe_allow_html=True)
        st.markdown(f"**Bedroom Doors:** <span style='color:{GOLD}'>800 x 2100 mm</span> to 900 x 2100 mm", unsafe_allow_html=True)
        st.markdown(f"**Bathroom Doors:** <span style='color:{GOLD}'>700 x 2100 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Corridor Width:** <span style='color:{GOLD}'>1050 mm</span> (Min) for residential passage.", unsafe_allow_html=True)
        st.markdown(f"**Staircase Width:** <span style='color:{GOLD}'>900 mm</span> (Min residential clearance)", unsafe_allow_html=True)
        st.markdown(f"**Stair Riser/Tread:** Riser <span style='color:{GOLD}'>150-190 mm</span> | Tread <span style='color:{GOLD}'>250-300 mm</span>", unsafe_allow_html=True)

    with st.expander("🛋️ Furniture Dimensions Reference"):
        st.markdown(f"**King Bed:** <span style='color:{GOLD}'>1930 x 2030 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Queen Bed:** <span style='color:{GOLD}'>1520 x 2030 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Single Bed:** <span style='color:{GOLD}'>910 x 1880 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Wardrobe Depth:** <span style='color:{GOLD}'>600 mm</span> (Standard hanger clearance)", unsafe_allow_html=True)
        st.markdown(f"**Dining Table (4-Seater):** <span style='color:{GOLD}'>1200 x 750 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Dining Table (6-Seater):** <span style='color:{GOLD}'>1600 x 900 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Sofa (3-Seater):** <span style='color:{GOLD}'>1900 - 2100 x 850 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Kitchen Counter:** <span style='color:{GOLD}'>600 mm depth | 900 mm height</span>", unsafe_allow_html=True)

    with st.expander("📐 Minimum Residential Room Sizes (IS Code approximations)"):
        st.markdown(f"**Living Room:** <span style='color:{GOLD}'>3600 x 4200 mm</span> (15.12 sq.m)", unsafe_allow_html=True)
        st.markdown(f"**Master Bedroom:** <span style='color:{GOLD}'>3000 x 3600 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Children's Bedroom:** <span style='color:{GOLD}'>2700 x 3000 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Kitchen:** <span style='color:{GOLD}'>2400 x 3000 mm</span>", unsafe_allow_html=True)
        st.markdown(f"**Bathroom/WC Attached:** <span style='color:{GOLD}'>1500 x 1800 mm</span>", unsafe_allow_html=True)

    with st.expander("🕉️ Vastu Golden Proportions"):
        st.markdown(f"**Ideal Room Ratio:** <span style='color:{GOLD}'>1:1, 1:1.2, or 1:1.5</span> (Avoid ratios greater than 1:2 as they represent imbalance).", unsafe_allow_html=True)
        st.markdown(f"**Window to Floor Ratio:** Windows should equal <span style='color:{GOLD}'>at least 10%</span> of total floor area for adequate Prana (energy) flow.", unsafe_allow_html=True)
        st.markdown(f"**Main Door Proportion:** Height should be twice the width. Minimum height <span style='color:{GOLD}'>210 cm</span>.", unsafe_allow_html=True)
        st.markdown(f"**Plot Ratio:** Ideal plot depth should be equal or up to <span style='color:{GOLD}'>1.5x</span> the frontage (Gaumukhi or Shermukhi depending on use).", unsafe_allow_html=True)
