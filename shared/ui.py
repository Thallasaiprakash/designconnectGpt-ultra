import streamlit as st

GOLD = "#C9A84C"
NAVY = "#07101E"
NAVY2 = "#0D1B2E"
CREAM = "#F5EDD6"
JADE = "#4FAD88"
DANGER = "#E05050"
AMBER = "#E8A030"

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Outfit:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(201,168,76,0.025) 60px, rgba(201,168,76,0.025) 61px),
        repeating-linear-gradient(90deg, transparent, transparent 60px, rgba(201,168,76,0.025) 60px, rgba(201,168,76,0.025) 61px);
    pointer-events: none;
    z-index: 0;
}

.premium-card {
    background: #0D1B2E;
    border: 0.5px solid rgba(201,168,76,0.2);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    position: relative;
}
.premium-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #C9A84C, transparent);
    opacity: 0.5;
    border-radius: 14px 14px 0 0;
}

.gold-divider { width: 100px; height: 1px; background: linear-gradient(90deg, transparent, #C9A84C, transparent); margin: 16px auto; }

.om-glow { font-size: 48px; text-align: center; filter: drop-shadow(0 0 20px rgba(201,168,76,0.6)); animation: pulse 3s ease-in-out infinite; }
@keyframes pulse { 0%,100%{filter:drop-shadow(0 0 12px rgba(201,168,76,0.4))} 50%{filter:drop-shadow(0 0 28px rgba(201,168,76,0.9))} }

[data-testid="metric-container"] { background: #0D1B2E; border: 0.5px solid rgba(201,168,76,0.2); border-radius: 12px; padding: 16px !important; }
[data-testid="stMetricValue"] { color: #C9A84C !important; font-family: 'Cormorant Garamond', serif !important; font-size: 2.2rem !important; }

.stButton > button {
    background: linear-gradient(135deg, #C9A84C, #E07B30) !important;
    color: #07101E !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-family: 'Outfit', sans-serif !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(201,168,76,0.35) !important; }

.streamlit-expanderHeader { color: #C9A84C !important; font-weight: 500 !important; }

[data-testid="stSidebar"] { background: #07101E !important; border-right: 0.5px solid rgba(201,168,76,0.15) !important; }
[data-testid="stSidebar"] * { color: #F5EDD6 !important; }

.stProgress > div > div { background: linear-gradient(90deg, #C9A84C, #E07B30) !important; }

.stSuccess { background: rgba(79,173,136,0.1) !important; border: 0.5px solid rgba(79,173,136,0.3) !important; color: #4FAD88 !important; }
.stWarning { background: rgba(232,160,48,0.1) !important; border: 0.5px solid rgba(232,160,48,0.3) !important; }
.stError { background: rgba(224,80,80,0.1) !important; border: 0.5px solid rgba(224,80,80,0.3) !important; }
</style>
"""

def inject_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def page_header(icon: str, title: str, subtitle: str):
    inject_css()
    st.markdown(f'<div class="om-glow">{icon}</div>', unsafe_allow_html=True)
    st.markdown(f'<h1 style="font-family:Cormorant Garamond,serif;text-align:center;color:#F5EDD6;font-size:2.4rem;font-weight:600;margin-bottom:4px">{title}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:#6B8099;font-size:15px;margin-bottom:0">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

def gold_card(content_html: str):
    st.markdown(f'<div class="premium-card">{content_html}</div>', unsafe_allow_html=True)

def section_title(text: str):
    st.markdown(f'<p style="font-size:11px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;color:#6B8099;margin:18px 0 8px">{text}</p>', unsafe_allow_html=True)
