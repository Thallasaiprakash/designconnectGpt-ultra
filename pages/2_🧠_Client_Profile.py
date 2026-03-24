import streamlit as st
import json
import base64
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from shared.ui import page_header, inject_css, section_title, gold_card
from shared.ai_client import ask_ai

st.set_page_config(page_title="Client Profile AI", layout="wide", page_icon="🧠")
inject_css()

page_header("🧠", "Client Profile AI", "Psychological design profiling & revision predictor")

if 'cp_step' not in st.session_state:
    st.session_state.cp_step = 0
if 'cp_answers' not in st.session_state:
    st.session_state.cp_answers = []
if 'cp_client' not in st.session_state:
    st.session_state.cp_client = ""
if 'cp_designer' not in st.session_state:
    st.session_state.cp_designer = ""
if 'cp_notes' not in st.session_state:
    st.session_state.cp_notes = ""
if 'cp_results' not in st.session_state:
    st.session_state.cp_results = None

QUESTIONS = [
    {
        "q": "When you walk into a room you love, what hits you FIRST?",
        "options": [
            "The warmth — soft textures and coziness",
            "The order — clean lines, nothing out of place",
            "The personality — art, colour, unexpected details",
            "The space — openness and airiness"
        ]
    },
    {
        "q": "Ideal Sunday morning at home looks like:",
        "options": [
            "Quiet corner, warm coffee, total stillness",
            "Sunlit open space, family together",
            "Minimal and meditative, almost nothing visible",
            "Layered and cosy, books and objects everywhere"
        ]
    },
    {
        "q": "Designer shows two rooms. Room A is perfectly styled like a luxury hotel. Room B is personal but slightly imperfect. You choose:",
        "options": [
            "Room A — I want everything polished",
            "Room B — I want character over perfection",
            "Depends on the specific room",
            "I want both perfection AND personality"
        ]
    },
    {
        "q": "When stressed at home, which environment helps you recover?",
        "options": [
            "Nearly empty room, total simplicity",
            "Warm enclosed space, like a cocoon",
            "Outdoors connection, plants and natural light",
            "Familiar objects with memory and meaning"
        ]
    },
    {
        "q": "Your honest reaction to bold colours — deep teal wall, burgundy sofa:",
        "options": [
            "Yes please, I want drama",
            "One statement piece, rest stays neutral",
            "Texture over colour, colour makes me anxious",
            "I love them in theory but won't live with them"
        ]
    },
    {
        "q": "Designer presents concept. You love 70% but one element bothers you. You:",
        "options": [
            "Say nothing, trust the expert",
            "Mention it politely",
            "Ask to redo that element immediately",
            "Approve it but keep thinking about it"
        ]
    },
    {
        "q": "How do you make big decisions?",
        "options": [
            "Gut instinct first, justify later",
            "Research everything, decide on facts",
            "Ask people I trust, let them guide me",
            "Delay as long as possible, decide under pressure"
        ]
    }
]

def reset_profile():
    st.session_state.cp_step = 0
    st.session_state.cp_answers = []
    st.session_state.cp_notes = ""
    st.session_state.cp_results = None
    st.rerun()

if st.session_state.cp_step == 0:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gold_card("<div style='text-align:center'><h3>7 quick questions → psychological design profile → designer brief</h3></div>")
        st.session_state.cp_client = st.text_input("Client Name", value=st.session_state.cp_client)
        st.session_state.cp_designer = st.text_input("Designer Name", value=st.session_state.cp_designer)
        st.session_state.cp_notes = st.text_area("Optional: Paste any conversational notes, emails, or chat history with the client to run Deep NLP Sentiment Analysis on.", value=st.session_state.cp_notes, height=100)
        if st.button("Start Profiling", use_container_width=True, type="primary"):
            if not st.session_state.cp_client:
                st.warning("Please enter client name.")
            else:
                st.session_state.cp_step = 1
                st.rerun()

elif 1 <= st.session_state.cp_step <= 7:
    idx = st.session_state.cp_step - 1
    q_data = QUESTIONS[idx]
    
    st.progress(st.session_state.cp_step / 7.0, text=f"Question {st.session_state.cp_step} of 7")
    st.markdown(f"<h2 style='font-family:Cormorant Garamond,serif;text-align:center;padding:40px 0'>{q_data['q']}</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    opts = q_data['options']
    
    def answer(opt_text):
        st.session_state.cp_answers.append({"q": q_data['q'], "a": opt_text})
        st.session_state.cp_step += 1
    
    if c1.button(opts[0], use_container_width=True):
        answer(opts[0])
        st.rerun()
    if c2.button(opts[1], use_container_width=True):
        answer(opts[1])
        st.rerun()
    if c1.button(opts[2], use_container_width=True):
        answer(opts[2])
        st.rerun()
    if c2.button(opts[3], use_container_width=True):
        answer(opts[3])
        st.rerun()

elif st.session_state.cp_step == 8:
    if st.session_state.cp_results is None:
        with st.spinner("Running Deep Sentiment Analysis & NLP Profiling..."):
            prompt = f"""
            Analyze these 7 design psychology questions answered by the client:
            {json.dumps(st.session_state.cp_answers, indent=2)}
            
            Additionally, perform Deep NLP and Sentiment Analysis on these conversational notes provided by the designer:
            "{st.session_state.cp_notes}"
            
            Synthesize all of this into a profound psychological design brief.
            Return ONLY a JSON response in this exact format, with no markdown code blocks around it:
            {{
              "sentiment_analysis": "1-2 sentence NLP deep dive into their emotional state and true hidden desires",
              "personality_summary": "2-3 sentence portrait",
              "design_style_match": "2-3 specific design styles",
              "will_love": ["4 specific design decisions client will approve"],
              "will_resist": ["4 specific design decisions client will push back on"],
              "revision_risk": "Low/Medium/High",
              "revision_risk_reason": "1 sentence string",
              "presentation_tips": ["3 tips for presenting to THIS client"],
              "colors_to_use": "specific color direction",
              "colors_to_avoid": "specific colors to avoid",
              "decision_style": "emotional/analytical/social/pressure-driven",
              "red_flags": ["2 warning signs with this client type"],
              "trait_scores": {{"Warmth Seeker": 75, "Perfectionist": 40, "Bold Preference": 20, "Revision Risk": 65, "Social Focus": 55, "Sensory Sensitivity": 80, "Nostalgia": 45, "Decision Speed": 30}}
            }}
            """
            sys = "You are an elite AI Design Psychologist and NLP Sentiment Analyst. You use deep learning principles to decode human emotions, predicting hidden design preferences, behavioral red flags, and exact aesthetic desires with profound emotional intelligence to help architecture employees."
            res = ask_ai(prompt, system=sys, expect_json=True)
            try:
                data = json.loads(res)
                is_valid = True
            except:
                is_valid = False
                
            if not is_valid:
                st.error("Failed to parse AI response.")
                st.write(res)
                if st.button("Retry", key="retry_btn_1"):
                    st.rerun()
                st.stop()
                
            if "error" in data:
                st.error(f"🧠 AI API Error: {data['error']}")
                if st.button("Retry", key="retry_btn_2"):
                    st.rerun()
                st.stop()
                
            st.session_state.cp_results = data
    
    data = st.session_state.cp_results
    
    ps = data.get('personality_summary', 'Personality summary not available.')
    sa = data.get('sentiment_analysis', 'Data not available.')
    gold_card(f"<div style='font-size:18px'><b>{st.session_state.cp_client}'s Deep Profile:</b><br/>{ps}<br/><br/><b>🧠 NLP Sentiment Analysis:</b><br/>{sa}</div>")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Revision Risk", data.get("revision_risk", "Unknown"))
    m2.metric("Decision Style", data.get("decision_style", "Unknown").title())
    m3.metric("Best Style Match", data.get("design_style_match", "Unknown"))
    
    st.info(f"**Risk Reason:** {data.get('revision_risk_reason', 'Not provided.')}")
    
    c1, c2 = st.columns(2)
    with c1:
        section_title("Trait Scores")
        for trait, score in data.get("trait_scores", {}).items():
            st.write(f"**{trait}**")
            st.progress(score / 100.0)
            
        section_title("Color Psychology")
        st.success(f"**Use:** {data.get('colors_to_use', 'Any')}")
        st.error(f"**Avoid:** {data.get('colors_to_avoid', 'None')}")
        
    with c2:
        section_title("What they will LOVE")
        for item in data.get("will_love", []):
            st.markdown(f"✅ <span style='color:#4FAD88'>{item}</span>", unsafe_allow_html=True)
            
        section_title("What they will RESIST")
        for item in data.get("will_resist", []):
            st.markdown(f"❌ <span style='color:#E05050'>{item}</span>", unsafe_allow_html=True)
            
        section_title("Presentation Tips")
        for tip in data.get("presentation_tips", []):
            st.info(tip)
            
        if data.get("red_flags"):
            section_title("Red Flags")
            for flag in data.get("red_flags", []):
                st.warning(flag)
    
    st.markdown("---")
    colA, colB = st.columns(2)
    
    def create_pdf(data_dict, client, designer):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(50, 800, f"Client Profile Brief: {client}")
        p.setFont("Helvetica", 10)
        p.drawString(50, 780, f"Designer: {designer}")
        p.drawString(50, 760, f"Match: {data_dict.get('design_style_match', '')} | Risk: {data_dict.get('revision_risk', '')}")
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, 720, "Personality Summary:")
        p.setFont("Helvetica", 10)
        
        y = 700
        import textwrap
        lines = textwrap.wrap(data_dict.get('personality_summary', ''), width=90)
        for l in lines:
            p.drawString(50, y, l)
            y -= 15
            
        y -= 20
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Will Love:")
        y -= 15
        p.setFont("Helvetica", 10)
        for item in data_dict.get('will_love', []):
            p.drawString(60, y, f"- {item}")
            y -= 15
            
        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Will Resist:")
        y -= 15
        p.setFont("Helvetica", 10)
        for item in data_dict.get('will_resist', []):
            p.drawString(60, y, f"- {item}")
            y -= 15
            
        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Presentation Tips:")
        y -= 15
        p.setFont("Helvetica", 10)
        for tip in data_dict.get('presentation_tips', []):
            p.drawString(60, y, f"- {tip}")
            y -= 15

        p.save()
        buffer.seek(0)
        return buffer

    pdf_bytes = create_pdf(data, st.session_state.cp_client, st.session_state.cp_designer)
    colA.download_button("📄 Download Designer Brief (PDF)", data=pdf_bytes, file_name=f"{st.session_state.cp_client}_Profile.pdf", mime="application/pdf")
    
    if colB.button("New Client Profile", type="primary"):
        reset_profile()
