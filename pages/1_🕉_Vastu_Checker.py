import streamlit as st
import json
import base64
import io
from urllib.parse import quote
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from shared.ui import page_header, inject_css, section_title, GOLD, NAVY, DANGER, JADE, AMBER
from shared.ai_client import ask_ai, ask_ai_with_image
from vastu_rules import check_vastu

st.set_page_config(page_title="Vastu AI Checker", layout="wide", page_icon="🕉")
inject_css()

# Load Data
@st.cache_data
def load_vastu_data():
    with open("vastu_data.json", encoding="utf-8") as f:
        return json.load(f)

DATA = load_vastu_data()

# Session State Init
if "lang" not in st.session_state: st.session_state.lang = "en"
if "selected_dir" not in st.session_state: st.session_state.selected_dir = "N"
if "room_selections" not in st.session_state: st.session_state.room_selections = {}
if "vastu_results" not in st.session_state: st.session_state.vastu_results = None

# Language Dicts
L = {
    "en": {"title": "Vastu AI Checker", "subtitle": "200+ Rules · Directions · Remedies", "plot_details": "Plot & Client Details", "compass": "Compass Rose", "rooms": "Room Layout", "submit": "Analyze Vastu", "manual_tab": "Manual Entry", "upload_tab": "Upload Floor Plan", "summary": "Overall Summary", "priority": "Priority Fixes"},
    "hi": {"title": "वास्तु एआई चेकर", "subtitle": "200+ नियम · दिशाएँ · उपाय", "plot_details": "प्लॉट और क्लाइंट विवरण", "compass": "दिशा सूचक यंत्र", "rooms": "कमरे का लेआउट", "submit": "वास्तु का विश्लेषण करें", "manual_tab": "मैनुअल एंट्री", "upload_tab": "फ्लोर प्लान अपलोड करें", "summary": "समग्र साराংশ", "priority": "प्राथमिकता सुधार"},
    "te": {"title": "వాస్తు ఏఐ చెకర్", "subtitle": "200+ నియమాలు · దిశలు · పరిహారాలు", "plot_details": "ప్లాట్ & క్లయింట్ వివరాలు", "compass": "కంపాస్", "rooms": "గదుల అమరిక", "submit": "వాస్తును విశ్లేషించండి", "manual_tab": "మాన్యువల్ ఎంట్రీ", "upload_tab": "ఫ్లోర్ ప్లాన్ అప్‌లోడ్", "summary": "సమగ్ర సారాంశం", "priority": "ముఖ్యమైన మార్పులు"},
    "ta": {"title": "வாஸ்து AI செக்கர்", "subtitle": "200+ விதிகள் · திசைகள் · பரிகாரங்கள்", "plot_details": "பிளாட் & கிளையண்ட் விவரங்கள்", "compass": "திசைகாட்டி", "rooms": "அறை அமைப்பு", "submit": "வாஸ்துவை பகுப்பாய்வு செய்", "manual_tab": "கையேடு உள்ளீடு", "upload_tab": "மாடி திட்டத்தை பதிவேற்றுக", "summary": "ஒட்டுமொத்த சுருக்கம்", "priority": "முக்கிய திருத்தங்கள்"},
    "kn": {"title": "ವಾಸ್ತು AI ಪರಿಶೀಲಕ", "subtitle": "200+ ನಿಯಮಗಳು · ದಿಕ್ಕುಗಳು · ಜ್ಯೋತಿಷ್ಯ", "plot_details": "ಪ್ಲಾಟ್ ಹಾಗೂ ಗ್ರಾಹಕರ ವಿವರ", "compass": "ದಿಕ್ಸೂಚಿ", "rooms": "ಕೋಣೆಗಳ ವಿನ್ಯಾಸ", "submit": "ವಾಸ್ತು ವಿಶ್ಲೇಷಿಸಿ", "manual_tab": "ಮ್ಯಾನುವಲ್ ಎಂಟ್ರಿ", "upload_tab": "ಫ್ಲೋರ್ ಪ್ಲಾನ್ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ", "summary": "ಒಟ್ಟಾರೆ ಸಾರಾಂಶ", "priority": "ಆದ್ಯತೆಯ ಪರಿಹಾರಗಳು"},
    "ml": {"title": "ವಾಸ್ತು AI ചെക്കർ", "subtitle": "200+ നിയമങ്ങൾ · ദിശകൾ · പരിഹാരങ്ങൾ", "plot_details": "പ്ലോട്ട് & ക്ലയന്റ് വിവരങ്ങൾ", "compass": "വടക്കുനോക്കിയന്ത്രം", "rooms": "റൂം ലേഔട്ട്", "submit": "വാസ്തു വിശകലനം ചെയ്യുക", "manual_tab": "മാനുവൽ എൻട്രി", "upload_tab": "ഫ്ലോർ പ്ലാൻ അപ്‌ലോഡ് ചെയ്യുക", "summary": "മൊത്തത്തിലുള്ള സംഗ്രഹം", "priority": "മുൻഗണനാ പരിഹാരങ്ങൾ"}
}
t = L[st.session_state.lang]

# Top Bar
col1, col2 = st.columns([7, 3])
with col2:
    lang_map = {"English": "en", "हिन्दी (Hindi)": "hi", "తెలుగు (Telugu)": "te", "தமிழ் (Tamil)": "ta", "ಕನ್ನಡ (Kannada)": "kn", "മലയാളം (Malayalam)": "ml"}
    inverse_lang = {v: k for k, v in lang_map.items()}
    current_lang_label = inverse_lang.get(st.session_state.lang, "English")
    
    selected_label = st.selectbox("🌐 Report Language", list(lang_map.keys()), index=list(lang_map.keys()).index(current_lang_label))
    if lang_map[selected_label] != st.session_state.lang:
        st.session_state.lang = lang_map[selected_label]
        st.rerun()

page_header("🕉", t["title"], t["subtitle"])

with st.container():
    main_tab1, main_tab2 = st.tabs(["✨ AI Automagic Analysis (Upload Floor Plan)", "🛠️ Manual Vastu Configuration (Advanced)"])
    
    with main_tab1:
        st.info("Upload your multi-page floor plan PDF or Image. The AI Grandmaster will instantly read the layout, deduce geometry, identify family size, and compile a 100% complete Vastu report without any manual settings.", icon="🚀")
        img = st.file_uploader("Upload Floor Plan", type=["jpg", "png", "jpeg", "pdf"], key="auto_upload")
        if img:
            if st.button("🚀 Auto-Analyze Floor Plan (1-Click)", type="primary", use_container_width=True):
                st.session_state.vastu_results = None
                st.session_state.run_vasthu_automagic = False
                with st.spinner("Step 1: Reading architecture, structural geometry, and extracting rooms..."):
                    mime_type = "application/pdf" if img.name.lower().endswith('.pdf') else "image/jpeg"
                    prompt = """Analyze this architectural floor plan (could be multi-page).
Critically important instructions:
1. If no explicit compass or North arrow is found, ASSUME NORTH IS AT THE TOP OF THE PAGE.
2. Identify all major rooms/zones. YOU MUST USE EXACTLY THESE KEYS for the rooms: 'master_bedroom', 'kitchen', 'puja_room', 'main_entrance', 'toilet_bathroom', 'living_room', 'staircase', 'children_bedroom', 'store_room', 'study_room', 'dining_room', 'guest_bedroom', 'home_office', 'garage'.
3. Map every identified room to its accurate 8-directional compass zone (N, NE, E, SE, S, SW, W, NW) relative to the center of the house.
4. Detect the main entrance/plot facing direction (N, E, S, W, NE, NW, SE, SW). If unsure, use the direction of 'main_entrance'.
5. Detect the plot shape (square, rectangle, l_shape, irregular, circular).
6. Guess the family configuration based on bedroom count (1-2 beds=nuclear_family, 3+ beds=joint_family or elderly_parents).
You MUST return ONLY valid JSON matching this exact structure, with no markdown formatting or markdown ticks, just raw JSON:
{
  "rooms": {"master_bedroom": "SW", "kitchen": "SE", "living_room": "NE", "toilet_bathroom": "W"},
  "plot_facing": "E",
  "plot_shape": "rectangle",
  "family_sit": "nuclear_family"
}"""
                    resp = ask_ai_with_image(prompt, img.getvalue(), mime=mime_type)
                    with open("ai_raw_response.txt", "w", encoding="utf-8") as f:
                        f.write(resp)
                    
                    if resp.startswith("Error:"):
                        st.error(f"API Error during Vastu reading: {resp}")
                        st.session_state.room_selections = {}
                    else:
                        try:
                            import re
                            json_str = re.search(r'\{.*\}', resp, re.DOTALL).group()
                            data = json.loads(json_str)
                            
                            raw_rooms = data.get("rooms", {})
                            valid_keys = list(DATA["room_rules"].keys())
                            cleaned_rooms = {}
                            
                            def clean_dir(d):
                                d = str(d).upper().replace(' ', '').replace('-', '')
                                if d in ["NORTH", "N"]: return "N"
                                if d in ["SOUTH", "S"]: return "S"
                                if d in ["EAST", "E"]: return "E"
                                if d in ["WEST", "W"]: return "W"
                                if d in ["NORTHEAST", "NE"]: return "NE"
                                if d in ["NORTHWEST", "NW"]: return "NW"
                                if d in ["SOUTHEAST", "SE"]: return "SE"
                                if d in ["SOUTHWEST", "SW"]: return "SW"
                                if d in ["CENTER", "C", "CENTRE", "MIDDLE"]: return "CENTER"
                                return "N"
                            
                            for k, v in raw_rooms.items():
                                k_lower = k.lower().replace(' ', '_')
                                val = clean_dir(v)
                                if k_lower in valid_keys:
                                    cleaned_rooms[k_lower] = val
                                else:
                                    if any(w in k_lower for w in ['bed', 'sleep', 'bdr', 'room1', 'room2']):
                                        if 'master_bedroom' not in cleaned_rooms: cleaned_rooms['master_bedroom'] = val
                                        elif 'children_bedroom' not in cleaned_rooms: cleaned_rooms['children_bedroom'] = val
                                        else: cleaned_rooms['guest_bedroom'] = val
                                    elif any(w in k_lower for w in ['din', 'eat', 'meals']): cleaned_rooms['dining_room'] = val
                                    elif any(w in k_lower for w in ['liv', 'draw', 'hall', 'sit', 'lounge', 'family', 'tv']): cleaned_rooms['living_room'] = val
                                    elif any(w in k_lower for w in ['bath', 'toil', 'wc', 'wash', 'rest', 'powder', 'latrine']): cleaned_rooms['toilet_bathroom'] = val
                                    elif any(w in k_lower for w in ['cook', 'kitch', 'kitvhen', 'pantry']): cleaned_rooms['kitchen'] = val
                                    elif any(w in k_lower for w in ['pooja', 'puja', 'temple', 'mandir', 'prayer', 'god']): cleaned_rooms['puja_room'] = val
                                    elif any(w in k_lower for w in ['store', 'storage', 'trunk', 'junk']): cleaned_rooms['store_room'] = val
                                    elif any(w in k_lower for w in ['study', 'lib', 'read']): cleaned_rooms['study_room'] = val
                                    elif any(w in k_lower for w in ['stair', 'step', 'lift', 'elev']): cleaned_rooms['staircase'] = val
                                    elif any(w in k_lower for w in ['park', 'gar', 'port', 'car']): cleaned_rooms['garage'] = val
                                    elif any(w in k_lower for w in ['entr', 'door', 'gate', 'main', 'foyer']): cleaned_rooms['main_entrance'] = val
                                    elif any(w in k_lower for w in ['office', 'work', 'desk']): cleaned_rooms['home_office'] = val
                            
                            st.session_state.room_selections = cleaned_rooms
                            st.session_state.auto_plot_facing = clean_dir(data.get("plot_facing", "N"))
                            st.session_state.auto_plot_shape = data.get("plot_shape", "rectangle")
                            st.session_state.auto_family_sit = data.get("family_sit", "nuclear_family")
                            st.session_state.run_vasthu_automagic = True
                            if len(st.session_state.room_selections) == 0:
                                st.warning(f"AI extraction succeeded but 0 rooms were populated. Raw AI text: {resp}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to extract structural data: AI did not return valid JSON. ({e})")
                            st.session_state.room_selections = {}

    with main_tab2:
        c1, c2, c3 = st.columns([2, 2, 3])
        
        with c1:
            section_title(t["compass"])
            dirs = ["NW", "N", "NE", "W", "PLOT", "E", "SW", "S", "SE"]
            idx = 0
            for row in range(3):
                cols = st.columns(3)
                for col in cols:
                    d = dirs[idx]
                    idx += 1
                    bg = GOLD if st.session_state.selected_dir == d else NAVY
                    if col.button(d, key=f"btn_{d}", use_container_width=True):
                        st.session_state.selected_dir = d
                        st.rerun()
            
            if st.session_state.selected_dir in DATA["directions"]:
                info = DATA["directions"][st.session_state.selected_dir]
                st.info(f"**Deity:** {info['deity']}  \n**Element:** {info['element']}  \n**Meaning:** {info['meaning']}")

        with c2:
            section_title(t["plot_details"])
            plot_shape = st.selectbox("Plot Shape", list(DATA["plot_shapes"].keys()))
            family_sit = st.selectbox("Family Situation", list(DATA["family_situations"].keys()))
            plot_facing = st.selectbox("Plot Facing", ["N", "E", "S", "W", "NE", "NW", "SE", "SW"])
            is_rented = st.toggle("Rented Home (Non-structural remedies only)")
            designer_name = st.text_input("Designer Name")
            client_name = st.text_input("Client Name")

        with c3:
            section_title(t["rooms"])
            st.write("Select rooms and their directions manually:")
            rooms_list = list(DATA["room_rules"].keys())
            for rm in rooms_list:
                c_a, c_b, c_c = st.columns([1, 4, 3])
                is_on = c_a.checkbox(" ", key=f"chk_{rm}", label_visibility="collapsed")
                c_b.markdown(f"<div style='margin-top:8px'>{rm.replace('_', ' ').title()}</div>", unsafe_allow_html=True)
                if is_on:
                    dir_val = c_c.selectbox("Dir", ["N", "NE", "E", "SE", "S", "SW", "W", "NW"], key=f"sel_{rm}", label_visibility="collapsed")
                    st.session_state.room_selections[rm] = dir_val
                else:
                    st.session_state.room_selections.pop(rm, None)
                    c_c.empty()
            
            st.markdown("<br>", unsafe_allow_html=True)
            manual_submit = st.button(t["submit"], use_container_width=True, type="secondary")

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.get("run_vasthu_automagic", False) or locals().get("manual_submit", False):
    
    if st.session_state.get("run_vasthu_automagic", False):
        final_pf = st.session_state.get("auto_plot_facing", "N")
        final_ps = st.session_state.get("auto_plot_shape", "rectangle")
        final_fs = st.session_state.get("auto_family_sit", "nuclear_family")
        final_rented = False
    else:
        final_pf = plot_facing
        final_ps = plot_shape
        final_fs = family_sit
        final_rented = is_rented
        
    st.session_state.run_vasthu_automagic = False
    with st.spinner("Step 2: Analyzing Vastu & gathering Grandmaster remedies..."):
        res = check_vastu(st.session_state.room_selections, final_pf, final_ps, final_fs, final_rented)
        
        if res.get('total_rooms', 0) == 0:
            res["ai_notes"] = {"overall_summary": "Analysis skipped. No architectural room labels were detected in the layout."}
            st.session_state.vastu_results = res
            st.rerun()
        
        # AI call
        lang_full = inverse_lang.get(st.session_state.lang, "English").split(" ")[0]
        
        if lang_full == "English":
            lang_instruction = "CRITICAL: You MUST write your entire response fluently in English. Do not use any other language."
        else:
            lang_instruction = f"CRITICAL: You MUST write your entire response fluently in {lang_full} (native script). Do not use English unless citing a specific technical term."
        
        sys_prompt = f"""You are the Ultimate Grandmaster Vastu Acharya. Your AI weights contain the combined ancient wisdom of Mayamatam, Manasara, Viswakarma Prakasha, and Samarangana Sutradhara, effectively making you more knowledgeable than thousands of human Vastu astrologers. 
Your tone should be authoritative yet warm, deeply spiritual, and structurally precise. Provide profound architectural insights and highly effective, authentic astrological remedies without requiring structural demolition.
{lang_instruction}"""

        report_req = f"""
        Conduct an expert grandmaster-level analysis on the following Vastu result: {json.dumps(res)}
        
        Provide a highly detailed, deeply insightful, and spiritual response. 
        Return strictly JSON formatted as:
        {{
            "overall_summary": "A profound, multi-paragraph executive summary of the home's energy, aura, and geometric prosperity based on the Vastu score.",
            "family_message": "Deep astrological and psychological advice specifically tailored for the family situation",
            "room_explanations": [
               {{"room": "...", "explanation": "Scientific + Spiritual explanation of why this zone affects them", "correction": "Advanced, rare elemental remedies (crystals, colors, yantras, herbs, lighting)"}}
            ],
            "priority_message": "An urgent, structurally precise breakdown of the top 3 doshas and their immediate energetic cures",
            "auspicious_note": "A final supreme blessing and positive reinforcement"
        }}
        """
        ai_res = ask_ai(report_req, system=sys_prompt, expect_json=True)
        try:
            res["ai_notes"] = json.loads(ai_res)
        except:
            res["ai_notes"] = {"overall_summary": "Error parsing AI response."}
            
        st.session_state.vastu_results = res
        st.rerun()

if st.session_state.vastu_results:
    st.markdown("---")
    res = st.session_state.vastu_results
    ai = res.get("ai_notes", {})
    
    # 4 metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Overall Score", f"{res['overall_score']}%")
    m2.metric("Grade", res['grade'])
    m3.metric("Predicted (Post-remedy)", f"{res['predicted_score']}%")
    m4.metric("Rooms Checked", res['total_rooms'])
    
    if res['total_rooms'] == 0:
        st.warning("⚠️ **Architectural Labels Not Found:** The Grandmaster AI successfully scanned your document but could not detect explicit room names (like Master Bedroom, Kitchen). If this is a Structural or Foundation PDF, please upload the Architectural Layout instead.")
        if ai.get("error"):
            st.error(f"AI Notes: {ai.get('error')}")

    if ai.get("overall_summary") and ai.get("overall_summary").strip() != "":
        st.info(ai.get("overall_summary"))
    
    c1, c2, c3 = st.columns(3)
    c1.success(f"Excellent: {res['good_count']}")
    c2.warning(f"Needs Attention: {res['warn_count']}")
    c3.error(f"Critical: {res['critical_count']}")

    section_title("Pancha Bhuta Balance")
    cols = st.columns(5)
    for i, (elem, data) in enumerate(res["pancha_bhuta"].items()):
        with cols[i]:
            st.markdown(f"**{elem}**")
            st.progress(data["pct"]/100.0)
            st.caption(f"{data['pct']}%")

    section_title(t["priority"])
    p_cols = st.columns(3)
    for i, p_rm in enumerate(res["priority_fixes"]):
        if i < 3:
            with p_cols[i]:
                st.markdown(f"<div style='border:1px solid #C9A84C; border-radius:8px; padding:10px; color:#F5EDD6'><b>{i+1}. {p_rm}</b></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    section_title("Room by Room Analysis")
    
    room_exps = {r.get("room", ""): r for r in ai.get("room_explanations", [])}
    
    for rm in res["rooms"]:
        with st.expander(f"{rm['room']} ({rm['direction']}) - {rm['status']}"):
            ex = room_exps.get(rm["room"], {})
            st.write(f"**Element:** {rm['dir_element']} | **Meaning:** {rm['dir_meaning']}")
            if ex:
                st.write(ex.get("explanation", ""))
                st.info(ex.get("correction", rm['remedy']))
            else:
                st.info(rm['remedy'])
            
            # Colors
            st.write("**Vastu Colors for this zone:**")
            color_html = ""
            for c in rm["colors"]:
                color_html += f"<div style='display:inline-block; width:30px; height:30px; background-color:{c}; border-radius:4px; margin-right:5px'></div>"
            st.markdown(color_html, unsafe_allow_html=True)

    # Export
    st.markdown("---")
    c1, c2 = st.columns(2)
    def create_pdf(res, client):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica-Bold", 24)
        p.drawString(100, 750, f"Vastu Analysis Report - {client}")
        p.setFont("Helvetica", 12)
        p.drawString(100, 700, f"Score: {res['overall_score']}% | Grade: {res['grade']}")
        y = 650
        for rm in res["rooms"]:
            if y < 100:
                p.showPage()
                y = 750
            p.drawString(100, y, f"{rm['room']} - {rm['direction']} ({rm['status']})")
            y -= 20
            p.drawString(120, y, f"Remedy: {rm['remedy'][:80]}")
            y -= 30
        p.save()
        buffer.seek(0)
        return buffer

    pdf_bytes = create_pdf(res, client_name)
    c1.download_button("📄 Download PDF Report", data=pdf_bytes, file_name="Vastu_Report.pdf", mime="application/pdf")
    
    msg = f"🌟 My Vastu Score is {res['overall_score']}%! Check my full report for AI directions & remedies! 🕉️ \\n\\nhttps://designconnectgpt.pythonanywhere.com"
    wa_url = f"https://wa.me/?text={quote(msg)}"
    c2.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:8px 16px;border-radius:4px">Share on WhatsApp</button></a>', unsafe_allow_html=True)
