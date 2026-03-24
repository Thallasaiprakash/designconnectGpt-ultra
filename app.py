import streamlit as st
from shared.ui import inject_css

st.set_page_config(
    page_title="DesignConnectGPT ULTRA",
    page_icon="🕉",
    layout="wide",
    initial_sidebar_state="expanded"
)
inject_css()

with st.sidebar:
    st.markdown('<div style="text-align:center;padding:20px 0 10px"><span style="font-size:32px">🕉</span><br><span style="font-family:Cormorant Garamond,serif;color:#C9A84C;font-size:18px;font-weight:600">DesignConnectGPT</span><br><span style="font-size:11px;color:#6B8099">ULTRA</span></div>', unsafe_allow_html=True)
    from shared.ui import model_selector
    model_selector()
    st.markdown('<hr style="border-color:rgba(201,168,76,0.15)">', unsafe_allow_html=True)

st.markdown('<h1 style="font-family:Cormorant Garamond,serif;text-align:center;color:#F5EDD6;font-size:3rem;font-weight:600">DesignConnect<span style="color:#C9A84C">GPT</span> ULTRA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#6B8099;font-size:16px;margin-bottom:32px">India\'s first complete AI platform for interior designers · 8 powerful modules · 100% free</p>', unsafe_allow_html=True)

modules = [
    ("pages/1_🕉_Vastu_Checker.py", "🕉️", "Vastu AI Checker", "200+ rules · Hindi/English · PDF report"),
    ("pages/2_🧠_Client_Profile.py", "🧠", "Client Profile AI", "Emotional profiling · revision predictor"),
    ("pages/3_🎨_Render_Engine.py", "🎨", "AI Render Engine", "Text/Image → photorealistic renders · Free"),
    ("pages/4_🏠_Room_Staging.py", "🏠", "Room Staging AI", "Upload room photo → see it redesigned"),
    ("pages/5_📐_Space_Planning.py", "📐", "Space Planning", "Layouts · furniture · circulation zones"),
    ("pages/6_💰_BOQ_Estimator.py", "💰", "BOQ Estimator", "Bill of quantities · Indian market rates"),
    ("pages/7_💡_Lighting_Plan.py", "💡", "Lighting Plan", "Fixture types · lux levels · CCT values"),
    ("pages/8_📋_CAD_Guidance.py", "📋", "CAD Guidance", "AutoCAD commands · DXF generation"),
]
cols = st.columns(4)
for i, (path, icon, name, desc) in enumerate(modules):
    with cols[i % 4]:
        st.markdown(f'<div class="premium-card" style="text-align:center; height:130px"><div style="font-size:28px;margin-bottom:8px">{icon}</div><div style="font-family:Cormorant Garamond,serif;font-size:16px;color:#F5EDD6;font-weight:600;margin-bottom:4px">{name}</div><div style="font-size:11px;color:#6B8099">{desc}</div></div>', unsafe_allow_html=True)
        if st.button(f"Open {name}", key=f"btn_{i}", use_container_width=True):
            st.switch_page(path)
