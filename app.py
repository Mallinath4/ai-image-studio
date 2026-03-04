import os
import io
import time
import random
import zipfile
import json
from pathlib import Path
import logging

import streamlit as st
from PIL import Image

logging.getLogger("tornado.access").setLevel(logging.ERROR)
logging.getLogger("tornado.application").setLevel(logging.ERROR)
logging.getLogger("tornado.general").setLevel(logging.ERROR)

st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    css_path = Path("assets/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*, html, body {
    font-family: 'Inter', sans-serif !important;
}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #06060f !important;
}
[data-testid="stHeader"] { background: transparent !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a1a 0%, #080812 100%) !important;
    border-right: 1px solid rgba(167,139,250,0.08) !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background:
        radial-gradient(ellipse at 10% 30%, rgba(124,58,237,0.22) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 10%, rgba(59,130,246,0.16) 0%, transparent 50%),
        radial-gradient(ellipse at 60% 90%, rgba(16,185,129,0.12) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0.97) 0%, #06060f 100%);
    pointer-events: none;
    z-index: 0;
}

@keyframes floatLogo {
    0%,100% { transform: translateY(0px) rotate(-2deg); filter: drop-shadow(0 0 28px rgba(167,139,250,0.8)); }
    50%      { transform: translateY(-10px) rotate(2deg); filter: drop-shadow(0 0 48px rgba(167,139,250,1.0)); }
}
@keyframes shimmer {
    0%   { background-position: -200% center; }
    100% { background-position: 200% center; }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse-border {
    0%,100% { box-shadow: 0 0 0 1px rgba(167,139,250,0.2), 0 20px 60px rgba(0,0,0,0.6); }
    50%      { box-shadow: 0 0 0 1px rgba(167,139,250,0.4), 0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(124,58,237,0.15); }
}

.logo-glow {
    display: inline-block;
    font-size: 5rem;
    animation: floatLogo 4s ease-in-out infinite;
    filter: drop-shadow(0 0 28px rgba(167,139,250,0.8));
}

.brand-title {
    font-size: 3rem !important;
    font-weight: 900 !important;
    background: linear-gradient(135deg, #e879f9 0%, #a78bfa 30%, #60a5fa 65%, #34d399 100%);
    background-size: 200% auto;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -2.5px;
    line-height: 1.05;
    animation: shimmer 4s linear infinite;
    margin: 0 !important;
}
.brand-tagline {
    font-size: 15px;
    color: #64748b;
    margin: 10px 0 20px 0;
    line-height: 1.8;
    letter-spacing: 0.1px;
}

.feature-pills {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 8px;
}
.pill {
    padding: 6px 16px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
    transition: all 0.25s ease;
    cursor: default;
}
.pill:hover { transform: translateY(-3px); }
.pill-purple { background: rgba(192,132,252,0.12); color: #c084fc; border: 1px solid rgba(192,132,252,0.35); box-shadow: 0 0 16px rgba(192,132,252,0.12); }
.pill-blue   { background: rgba(96,165,250,0.10);  color: #60a5fa; border: 1px solid rgba(96,165,250,0.3);   box-shadow: 0 0 16px rgba(96,165,250,0.1); }
.pill-green  { background: rgba(52,211,153,0.10);  color: #34d399; border: 1px solid rgba(52,211,153,0.3);   box-shadow: 0 0 16px rgba(52,211,153,0.1); }
.pill-orange { background: rgba(251,191,36,0.10);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3);   box-shadow: 0 0 16px rgba(251,191,36,0.1); }

.auth-card {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(167,139,250,0.18) !important;
    border-radius: 28px !important;
    padding: 36px 32px 30px 32px !important;
    backdrop-filter: blur(40px) !important;
    -webkit-backdrop-filter: blur(40px) !important;
    animation: pulse-border 4s ease-in-out infinite;
    margin-top: 16px !important;
    position: relative;
}
.auth-card::before {
    content: "";
    position: absolute;
    top: -1px; left: 15%; right: 15%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(192,132,252,0.7), transparent);
    border-radius: 100%;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.025) !important;
    border-radius: 16px !important;
    padding: 5px !important;
    gap: 3px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 10px 24px !important;
    color: #475569 !important;
    transition: all 0.25s ease !important;
    border: none !important;
    letter-spacing: 0.1px !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: #94a3b8 !important;
    background: rgba(255,255,255,0.04) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: linear-gradient(135deg,rgba(124,58,237,0.3),rgba(79,70,229,0.22)) !important;
    color: #c084fc !important;
    box-shadow: 0 0 0 1px rgba(192,132,252,0.35), 0 4px 16px rgba(124,58,237,0.25) !important;
}

[data-testid="stTextInput"] label,
[data-testid="stTextInput"] label p {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
    margin-bottom: 5px !important;
    letter-spacing: 0.1px !important;
}
[data-testid="stTextInput"] input {
    background: rgba(10,10,25,0.85) !important;
    border: 1.5px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-size: 14.5px !important;
    padding: 13px 18px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03) !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(192,132,252,0.55) !important;
    box-shadow: 0 0 0 3px rgba(192,132,252,0.1), 0 2px 12px rgba(0,0,0,0.35) !important;
    background: rgba(192,132,252,0.04) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #2d3748 !important; }

[data-testid="stTextArea"] textarea {
    background: rgba(10,10,25,0.85) !important;
    border: 1.5px solid rgba(255,255,255,0.07) !important;
    border-radius: 14px !important;
    color: #f1f5f9 !important;
    font-size: 14px !important;
    padding: 13px 18px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(192,132,252,0.55) !important;
    box-shadow: 0 0 0 3px rgba(192,132,252,0.1) !important;
}

[data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 60%, #3b82f6 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 16px !important;
    font-size: 15.5px !important;
    font-weight: 800 !important;
    padding: 15px 20px !important;
    letter-spacing: 0.4px !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.5), 0 0 0 1px rgba(167,139,250,0.25), inset 0 1px 0 rgba(255,255,255,0.18) !important;
    transition: all 0.3s ease !important;
    margin-top: 10px !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(135deg, #6d28d9 0%, #4338ca 60%, #2563eb 100%) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.65), 0 0 0 1px rgba(167,139,250,0.4) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stFormSubmitButton"] > button:active { transform: translateY(0) !important; }

[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    box-shadow: 0 4px 16px rgba(124,58,237,0.4) !important;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 24px rgba(124,58,237,0.55) !important;
}

.stats-row {
    display: flex;
    justify-content: space-around;
    margin: 24px 0 6px 0;
    padding: 18px 12px 6px 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.stat-item { text-align: center; }
.stat-number {
    font-size: 24px;
    font-weight: 900;
    background: linear-gradient(135deg, #e879f9, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
}
.stat-label {
    font-size: 10px;
    color: #334155;
    text-transform: uppercase;
    letter-spacing: 1.4px;
    margin-top: 5px;
    font-weight: 700;
}

.security-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: wrap;
    gap: 14px;
    margin-top: 18px;
    padding: 12px 18px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 14px;
    font-size: 11.5px;
    color: #334155;
    font-weight: 600;
}

.form-section-title {
    font-size: 22px;
    font-weight: 900;
    color: #f1f5f9;
    letter-spacing: -0.8px;
    margin-bottom: 4px;
    line-height: 1.2;
}
.form-section-sub {
    font-size: 13.5px;
    color: #475569;
    margin-bottom: 20px;
    line-height: 1.6;
}

[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: none !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
}

.profile-card {
    background: linear-gradient(135deg,rgba(124,58,237,0.18),rgba(79,70,229,0.1));
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 20px;
    padding: 22px 16px;
    text-align: center;
    margin-bottom: 16px;
    box-shadow: 0 4px 24px rgba(124,58,237,0.18), inset 0 1px 0 rgba(255,255,255,0.05);
    position: relative;
    overflow: hidden;
}
.profile-card::before {
    content: "";
    position: absolute;
    top: -1px; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(192,132,252,0.5), transparent);
}

.section-label {
    font-size: 11px;
    font-weight: 800;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}

.glass-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 20px;
    transition: all 0.25s ease;
}
.glass-card:hover {
    border-color: rgba(192,132,252,0.2);
    box-shadow: 0 4px 24px rgba(124,58,237,0.1);
}

.neg-prompt-box { background: rgba(239,68,68,0.04); border: 1px solid rgba(239,68,68,0.18); border-radius: 14px; padding: 14px 16px; margin-top: 8px; }
.batch-info { background: rgba(52,211,153,0.06); border: 1px solid rgba(52,211,153,0.2); border-radius: 14px; padding: 14px 18px; font-size: 13.5px; color: #6ee7b7; margin-bottom: 14px; }
.seed-grid-item { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 10px; transition: all 0.2s; }
.seed-grid-item:hover { border-color: rgba(192,132,252,0.3); box-shadow: 0 4px 20px rgba(124,58,237,0.12); }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); border-radius: 10px; }
::-webkit-scrollbar-thumb { background: rgba(167,139,250,0.25); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(167,139,250,0.45); }

[data-testid="stSidebar"] .stSlider label p,
[data-testid="stSidebar"] .stCheckbox label p,
[data-testid="stSidebar"] .stToggle label p {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
}

[data-testid="stCaptionContainer"] p {
    font-size: 12px !important;
    color: #475569 !important;
}

[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #94a3b8 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(192,132,252,0.08) !important;
    border-color: rgba(192,132,252,0.3) !important;
    color: #c084fc !important;
    transform: translateY(-1px) !important;
}

.page-title {
    font-size: 26px;
    font-weight: 900;
    color: #f1f5f9;
    letter-spacing: -1px;
    line-height: 1.2;
}
.page-sub {
    font-size: 14px;
    color: #475569;
    margin-top: 5px;
    line-height: 1.6;
}

[data-testid="stExpander"] summary svg title,
[data-testid="stExpander"] details svg title {
    display: none !important;
    visibility: hidden !important;
    font-size: 0 !important;
    color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ── Auth imports ──────────────────────────────────────────────────────────────
from auth.auth_handler import login_user, signup_user, update_gen_count

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in {
    "logged_in":            False,
    "user_data":            None,
    "selected_themes":      ["Realistic"],
    "selected_size":        "Medium",
    "gen_count":            0,
    "last_seed":            None,
    "last_time":            None,
    "results":              [],
    "seed_browser_results": [],
    "batch_results":        [],
    "library_search":       "",
    "neg_prompt_inject":    "",
    "show_examples":        False,
    "show_neg_prompt":      False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ═════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ═════════════════════════════════════════════════════════════════════════════
def show_auth_page():
    col_l, col_c, col_r = st.columns([1, 1.15, 1])
    with col_c:
        st.markdown("""
        <div style='text-align:center; padding: 52px 0 24px 0; animation: fadeInUp 0.6s ease;'>
            <div class='logo-glow'>🎨</div>
            <p class='brand-title'>AI Image Studio</p>
            <p class='brand-tagline'>
                Transform your imagination into stunning visuals<br>
                powered by state-of-the-art AI models
            </p>
            <div class='feature-pills'>
                <span class='pill pill-purple'>⚡ FLUX.1-schnell</span>
                <span class='pill pill-blue'>🧠 Mistral 7B</span>
                <span class='pill pill-green'>🗂️ RAG Memory</span>
                <span class='pill pill-orange'>📦 Batch Generate</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔑   Sign In", "✨   Create Account"])

        with tab_login:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='margin-bottom:20px;'>
                <div class='form-section-title'>Welcome back 👋</div>
                <div class='form-section-sub'>Sign in to continue generating amazing images</div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                email_or_user = st.text_input(
                    "📧 Email or Username",
                    placeholder="you@email.com or your username",
                    key="login_id"
                )
                password = st.text_input(
                    "🔒 Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_pass"
                )
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "🚀  Sign In to Studio",
                    width="stretch", type="primary"
                )
                if submitted:
                    if not email_or_user or not password:
                        st.error("❌ Please fill in all fields.")
                    else:
                        with st.spinner("Authenticating..."):
                            success, message, user_data = login_user(email_or_user, password)
                        if success:
                            st.session_state.logged_in = True
                            st.session_state.user_data = user_data
                            st.session_state.gen_count = user_data.get("gen_count", 0)
                            st.success(f"✅ {message}")
                            time.sleep(0.4)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

            st.markdown("""
            <div class='stats-row'>
                <div class='stat-item'>
                    <div class='stat-number'>12B</div>
                    <div class='stat-label'>Parameters</div>
                </div>
                <div class='stat-item'>
                    <div class='stat-number'>4</div>
                    <div class='stat-label'>Steps Only</div>
                </div>
                <div class='stat-item'>
                    <div class='stat-number'>16+</div>
                    <div class='stat-label'>Art Styles</div>
                </div>
                <div class='stat-item'>
                    <div class='stat-number'>Free</div>
                    <div class='stat-label'>Forever</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_signup:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style='margin-bottom:20px;'>
                <div class='form-section-title'>Create your account ✨</div>
                <div class='form-section-sub'>Join free and start generating stunning AI images today</div>
            </div>
            """, unsafe_allow_html=True)

            with st.form("signup_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    username = st.text_input("👤 Username", placeholder="your_username", key="su_user")
                with col_b:
                    email = st.text_input("📧 Email", placeholder="you@email.com", key="su_email")

                password = st.text_input(
                    "🔒 Password", type="password",
                    placeholder="Min. 6 characters", key="su_pass"
                )
                confirm = st.text_input(
                    "🔒 Confirm Password", type="password",
                    placeholder="Repeat your password", key="su_confirm"
                )

                if password:
                    length     = len(password)
                    has_upper  = any(c.isupper()          for c in password)
                    has_digit  = any(c.isdigit()          for c in password)
                    has_symbol = any(c in "!@#$%^&*()-_=" for c in password)
                    score = sum([length >= 6, length >= 10, has_upper, has_digit, has_symbol])
                    if score <= 1:   clr, lbl, pct = "#ef4444", "Weak",      "20%"
                    elif score == 2: clr, lbl, pct = "#f59e0b", "Fair",      "45%"
                    elif score == 3: clr, lbl, pct = "#60a5fa", "Good",      "70%"
                    else:            clr, lbl, pct = "#34d399", "Strong 💪", "100%"

                    st.markdown(
                        f"<div style='margin:-4px 0 14px 0;'>"
                        f"<div style='display:flex;justify-content:space-between;"
                        f"font-size:12px;margin-bottom:6px;'>"
                        f"<span style='color:#475569;font-weight:600;'>Password strength</span>"
                        f"<span style='color:{clr};font-weight:800;'>{lbl}</span></div>"
                        f"<div style='background:rgba(255,255,255,0.05);border-radius:100px;height:5px;'>"
                        f"<div style='width:{pct};height:5px;border-radius:100px;"
                        f"background:linear-gradient(90deg,{clr},{clr}cc);"
                        f"box-shadow:0 0 10px {clr}88;transition:all 0.4s ease;'></div></div></div>",
                        unsafe_allow_html=True
                    )

                    if confirm:
                        match = password == confirm
                        st.markdown(
                            f"<div style='font-size:12.5px;color:{'#34d399' if match else '#ef4444'};"
                            f"font-weight:700;margin:-4px 0 14px;'>"
                            f"{'✅ Passwords match' if match else '❌ Passwords do not match'}</div>",
                            unsafe_allow_html=True
                        )

                agree = st.checkbox("✅ I agree to the terms of use and privacy policy")
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button(
                    "🎉  Create Free Account",
                    width="stretch", type="primary"
                )
                if submitted:
                    if not agree:
                        st.warning("⚠️ Please agree to the terms first.")
                    else:
                        with st.spinner("Creating your account..."):
                            success, message = signup_user(username, email, password, confirm)
                        if success:
                            st.success(f"✅ {message}")
                            st.info("👆 Switch to the **Sign In** tab to login!")
                        else:
                            st.error(f"❌ {message}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class='security-badge'>
            <span>🔐 SHA-256 Encrypted</span>
            <span>💾 Stored Locally</span>
            <span>🚫 No Cloud Upload</span>
            <span>🆓 100% Free</span>
        </div>
        <div style='height:48px;'></div>
        """, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═════════════════════════════════════════════════════════════════════════════
def show_main_app():
    from pipeline.prompt_enhancer import enhance_prompt
    from pipeline.rag_store       import add_to_rag, get_rag_context_string, get_generation_history
    from pipeline.flux_generator  import generate_image, load_flux_pipeline
    from utils.image_utils        import save_image, image_to_bytes, get_download_filename

    THEMES = [
        ("None",       ""),
        ("Realistic",  "photorealistic, 8k, ultra detailed, natural lighting, sharp focus"),
        ("Animated",   "anime style, cel shading, vibrant colors, clean outlines"),
        ("Fairy Tale", "fairy-tale illustration, whimsical, storybook, dreamy colors"),
        ("Ancient",    "ancient painting, muted earthy tones, historical art style"),
        ("Jungle",     "lush jungle environment, dense foliage, atmospheric mist"),
        ("Futuristic", "futuristic sci-fi, sleek design, glowing tech, advanced cityscape"),
        ("Cyberpunk",  "cyberpunk city, neon lights, rain, dark alleys, high contrast"),
        ("Fantasy",    "epic fantasy art, magical atmosphere, dramatic lighting, painterly"),
        ("Horror",     "dark horror atmosphere, eerie shadows, unsettling, high contrast"),
        ("Mystical",   "mystical scene, glowing particles, soft fog, dreamy purple tones"),
        ("Watercolor", "watercolor painting, soft edges, paper texture, pastel palette"),
    ]
    THEME_ICONS = {
        "None":"🚫","Realistic":"🏔️","Animated":"🎬",
        "Fairy Tale":"🧚","Ancient":"🏛️","Jungle":"🌴",
        "Futuristic":"🚀","Cyberpunk":"🤖","Fantasy":"🐉",
        "Horror":"👻","Mystical":"🔮","Watercolor":"🖌️"
    }
    PRESET_SIZES = {
        "Tiny":      (256,  256),
        "Small":     (512,  512),
        "Medium":    (768,  768),
        "Large":     (1024, 1024),
        "Wide":      (1024, 768),
        "Tall":      (768,  1024),
        "HD Wide":   (1280, 720),
        "HD Tall":   (720,  1280),
        "Instagram": (1080, 1080),
        "Pinterest": (1000, 1500),
    }
    EXAMPLES = [
        "A majestic snow leopard on a mountain peak at golden hour",
        "Cyberpunk Tokyo street at night with neon rain reflections",
        "An ancient library with glowing books and floating candles",
        "A serene Japanese cherry blossom garden with koi pond",
        "Astronaut exploring an alien planet with two moons",
        "Steampunk airship flying above Victorian London at dusk",
    ]

    user = st.session_state.user_data

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class='profile-card'>
            <div style='width:60px;height:60px;
                 background:linear-gradient(135deg,#7c3aed,#4f46e5,#3b82f6);
                 border-radius:50%;display:flex;align-items:center;
                 justify-content:center;font-size:26px;margin:0 auto 14px auto;
                 box-shadow:0 4px 20px rgba(124,58,237,0.55);'>👤</div>
            <div style='font-size:16px;font-weight:900;color:#f1f5f9;letter-spacing:-0.5px;'>
                {user['username']}
            </div>
            <div style='font-size:12px;color:#475569;margin-top:4px;'>{user['email']}</div>
            <div style='margin-top:16px;padding-top:14px;
                 border-top:1px solid rgba(255,255,255,0.06);
                 display:flex;justify-content:center;gap:28px;'>
                <div style='text-align:center;'>
                    <div style='font-size:26px;font-weight:900;
                         background:linear-gradient(135deg,#e879f9,#60a5fa);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
                        {st.session_state.gen_count}
                    </div>
                    <div style='font-size:10px;color:#334155;text-transform:uppercase;
                         letter-spacing:1.2px;margin-top:3px;font-weight:700;'>
                         Images Generated
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", width="stretch", type="secondary"):
            for k in ["logged_in","user_data","results","selected_themes",
                      "gen_count","last_seed","last_time"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:16px 0;'>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>⚡ Quality</div>", unsafe_allow_html=True)
        quality = st.select_slider(
            "q", options=["draft","standard","high"],
            value="high", label_visibility="collapsed"
        )
        qmap = {
            "draft":    ("#f59e0b","⚡ Draft",    "1 step · Fastest"),
            "standard": ("#60a5fa","⚖️ Standard","3 steps · Balanced"),
            "high":     ("#34d399","🏆 High",     "4 steps · Best quality"),
        }
        qc, ql, qd = qmap[quality]
        st.markdown(
            f"<div style='padding:10px 14px;background:rgba(255,255,255,0.02);"
            f"border:1px solid rgba(255,255,255,0.06);border-radius:12px;margin-bottom:14px;'>"
            f"<span style='font-size:13.5px;font-weight:700;color:{qc};'>{ql}</span>"
            f"<span style='font-size:11.5px;color:#334155;margin-left:8px;'>{qd}</span></div>",
            unsafe_allow_html=True
        )

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>🎲 Seed Control</div>", unsafe_allow_html=True)
        use_random_seed = st.checkbox("Random seed", value=True)
        if use_random_seed:
            seed = -1
            st.caption("🎲 Unique result every time")
        else:
            seed = st.number_input("Fixed Seed", min_value=0, max_value=2**32-1, value=42)
            st.caption("🔒 Reproducible output")

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>🤖 AI Features</div>", unsafe_allow_html=True)
        use_reasoning = st.toggle("🧠 Mistral Reasoning", value=False)
        use_rag       = st.toggle("🗂️ RAG Memory",        value=True)

        sc = "#34d399" if use_reasoning else "#475569"
        sl = "✅ Mistral enhancing prompts" if use_reasoning else "ℹ️ Direct generation mode"
        st.markdown(
            f"<div style='padding:9px 13px;background:rgba(255,255,255,0.02);"
            f"border:1px solid rgba(255,255,255,0.05);border-radius:10px;"
            f"font-size:12.5px;color:{sc};margin-top:6px;line-height:1.5;'>{sl}</div>",
            unsafe_allow_html=True
        )

        st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:10px 0;'>", unsafe_allow_html=True)

        show_settings = st.toggle("⚙️ Settings", value=False, key="show_settings")
        if show_settings:
            st.markdown(
                "<div style='font-size:14px;font-weight:700;color:#94a3b8;margin-bottom:14px;'>"
                "🔐 Change Password</div>",
                unsafe_allow_html=True
            )
            with st.form("change_pw_form"):
                current_pw   = st.text_input("Current Password", type="password", key="cp_current")
                new_password = st.text_input("New Password",     type="password", key="cp_new")
                new_confirm  = st.text_input("Confirm New",      type="password", key="cp_confirm")

                if new_password and new_confirm:
                    match = new_password == new_confirm
                    st.markdown(
                        f"<div style='font-size:12px;color:{'#34d399' if match else '#ef4444'};"
                        f"font-weight:700;margin:-4px 0 12px;'>"
                        f"{'✅ Passwords match' if match else '❌ Do not match'}</div>",
                        unsafe_allow_html=True
                    )

                if st.form_submit_button("💾 Update Password", width="stretch"):
                    if not current_pw or not new_password or not new_confirm:
                        st.error("❌ Fill in all fields.")
                    elif new_password != new_confirm:
                        st.error("❌ Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("❌ Min. 6 characters.")
                    else:
                        from auth.auth_handler import change_password
                        ok, msg = change_password(user["user_id"], current_pw, new_password)
                        if ok: st.success(f"✅ {msg}")
                        else:  st.error(f"❌ {msg}")

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab_gen, tab_batch, tab_seeds, tab_gallery, tab_about = st.tabs([
        "🎨  Generate", "📦  Batch", "🌱  Seeds", "🖼️  Gallery", "ℹ️  About"
    ])

    # ── TAB 1: GENERATE ───────────────────────────────────────────────────────
    with tab_gen:
        st.markdown(f"""
        <div style='padding:30px 0 18px 0;text-align:center;'>
            <div style='font-size:30px;font-weight:900;color:#f1f5f9;letter-spacing:-1.5px;'>
                ✦ AI Image Studio
            </div>
            <div style='font-size:14.5px;color:#475569;margin-top:8px;line-height:1.6;'>
                Hello <b style='color:#c084fc;font-size:15px;'>{user['username']}</b>
                — Transform your ideas into stunning visuals ✨
            </div>
        </div>
        <hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin-bottom:22px;'>
        """, unsafe_allow_html=True)

        st.markdown(
            "<div class='section-label'>💬 Describe Your Image</div>",
            unsafe_allow_html=True
        )
        default_prompt = st.session_state.pop("inject_prompt", "")
        prompt = st.text_area(
            label="prompt", value=default_prompt,
            placeholder="e.g. A white cat sitting in a wooden chair near a window with soft sunlight...",
            height=115, label_visibility="collapsed"
        )

        if prompt.strip():
            words      = prompt.lower().split()
            word_count = len(words)
            has_subject   = any(w in prompt.lower() for w in ["cat","dog","woman","man","dragon","city","forest","mountain","robot","astronaut","castle","ocean","galaxy","warrior","wizard","person","animal"])
            has_lighting  = any(w in prompt.lower() for w in ["light","lighting","sunset","sunrise","golden hour","moonlight","neon","glow","shadow","backlit","volumetric"])
            has_style     = any(w in prompt.lower() for w in ["realistic","anime","painting","watercolor","digital art","oil","sketch","3d","cinematic","illustration","portrait"])
            has_mood      = any(w in prompt.lower() for w in ["dramatic","serene","mysterious","epic","dark","bright","foggy","peaceful","haunting","vibrant","moody"])
            has_camera    = any(w in prompt.lower() for w in ["close-up","wide angle","aerial","macro","bokeh","depth of field","8k","ultra detailed","sharp focus"])
            has_color     = any(w in prompt.lower() for w in ["blue","red","golden","purple","green","black","white","colorful","monochrome","pastel","vivid"])
            checks = [has_subject, has_lighting, has_style, has_mood, has_camera, has_color]
            score  = int((sum(checks) / len(checks)) * 100)
            if score >= 80:   bar_clr, grade = "#34d399", "Excellent 🔥"
            elif score >= 60: bar_clr, grade = "#60a5fa", "Good 👍"
            elif score >= 40: bar_clr, grade = "#f59e0b", "Fair ⚡"
            else:             bar_clr, grade = "#ef4444", "Weak 💡"

            st.markdown(
                f"<div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);"
                f"border-radius:14px;padding:12px 16px;margin:8px 0 14px 0;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:7px;'>"
                f"<span style='font-size:12px;font-weight:700;color:#64748b;'>🧠 Prompt Quality</span>"
                f"<span style='font-size:13px;font-weight:800;color:{bar_clr};'>{grade} · {score}/100</span></div>"
                f"<div style='background:rgba(255,255,255,0.05);border-radius:100px;height:5px;'>"
                f"<div style='width:{score}%;height:5px;border-radius:100px;"
                f"background:linear-gradient(90deg,{bar_clr},{bar_clr}aa);"
                f"box-shadow:0 0 10px {bar_clr}55;transition:all 0.4s;'></div></div>"
                f"<div style='font-size:11.5px;color:#334155;margin-top:7px;'>📝 {word_count} words</div>"
                f"</div>",
                unsafe_allow_html=True
            )

            suggestions = []
            if not has_lighting: suggestions.append(("💡 Lighting",  "golden hour lighting, soft volumetric light"))
            if not has_camera:   suggestions.append(("📷 Camera",    "8k, ultra detailed, sharp focus, depth of field"))
            if not has_mood:     suggestions.append(("🎭 Mood",      "dramatic atmosphere, cinematic feel"))
            if not has_color:    suggestions.append(("🎨 Color",     "vibrant colors, rich tones"))
            if not has_style:    suggestions.append(("🖌️ Style",    "digital art, highly detailed"))
            if suggestions:
                st.markdown(
                    "<div style='font-size:11px;font-weight:700;color:#475569;"
                    "text-transform:uppercase;letter-spacing:1.2px;margin-bottom:6px;'>"
                    "💡 Suggestions — click to add</div>",
                    unsafe_allow_html=True
                )
                cols_sug = st.columns(len(suggestions))
                for si, (label, value) in enumerate(suggestions):
                    with cols_sug[si]:
                        if st.button(label, key=f"sug_{si}", width="stretch"):
                            st.session_state["inject_prompt"] = f"{prompt}, {value}"
                            st.rerun()

        show_examples = st.toggle("💡 Show Example Prompts", value=False, key="show_examples")
        if show_examples:
            st.markdown(
                "<div style='background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);"
                "border-radius:14px;padding:12px 16px;margin-bottom:8px;'>",
                unsafe_allow_html=True
            )
            for ex in EXAMPLES:
                if st.button(f"📌 {ex}", key=f"ex_{ex[:20]}", width="stretch"):
                    st.session_state["inject_prompt"] = ex
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        show_neg = st.toggle("🚫 Add Negative Prompt", value=False, key="show_neg_prompt")
        if show_neg:
            st.markdown("<div class='neg-prompt-box'>", unsafe_allow_html=True)
            if "neg_prompt_inject" in st.session_state and st.session_state["neg_prompt_inject"]:
                st.session_state["neg_prompt"] = st.session_state.pop("neg_prompt_inject")
            negative_prompt = st.text_area(
                "neg", placeholder="e.g. blurry, ugly, distorted, low quality, watermark...",
                height=70, label_visibility="collapsed", key="neg_prompt"
            )
            neg_presets = ["blurry, ugly", "text, watermark", "distorted face", "low quality, noise"]
            cols_neg = st.columns(4)
            for i, np_val in enumerate(neg_presets):
                with cols_neg[i]:
                    if st.button(f"+ {np_val}", key=f"negp_{i}", width="stretch"):
                        current = st.session_state.get("neg_prompt", "")
                        st.session_state["neg_prompt_inject"] = f"{current}, {np_val}".strip(", ")
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            negative_prompt = ""

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>🎭 Choose Art Themes</div>", unsafe_allow_html=True)
        cols_t = st.columns(4)
        for i, (name, _) in enumerate(THEMES):
            with cols_t[i % 4]:
                checked = st.checkbox(
                    f"{THEME_ICONS.get(name,'⚪')} {name}",
                    value=(name in st.session_state.selected_themes),
                    key=f"chk_{name}"
                )
                if checked and name not in st.session_state.selected_themes:
                    st.session_state.selected_themes.append(name)
                elif not checked and name in st.session_state.selected_themes:
                    st.session_state.selected_themes.remove(name)

        selected_themes = st.session_state.selected_themes
        if not selected_themes:
            st.warning("⚠️ Select at least one theme.")
        else:
            icons_str = "  ·  ".join([f"{THEME_ICONS.get(t,'⚪')} {t}" for t in selected_themes])
            st.markdown(
                f"<div style='margin-top:10px;padding:10px 16px;"
                f"background:rgba(192,132,252,0.06);border-radius:12px;"
                f"font-size:13px;color:#c084fc;font-weight:700;"
                f"border:1px solid rgba(192,132,252,0.18);'>"
                f"✓ {len(selected_themes)} theme(s): {icons_str}</div>",
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<div class='section-label'>📐 Image Size</div>", unsafe_allow_html=True)
        size_tab_preset, size_tab_custom = st.tabs(["⚡ Preset Sizes", "✏️ Custom Size"])

        with size_tab_preset:
            cols_s = st.columns(5)
            for i, (label, (w, h)) in enumerate(PRESET_SIZES.items()):
                with cols_s[i % 5]:
                    is_sel = (st.session_state.selected_size == label)
                    if st.button(f"{label}\n{w}×{h}", key=f"size_{label}",
                                 width="stretch",
                                 type="primary" if is_sel else "secondary"):
                        st.session_state.selected_size = label
                        st.rerun()
            img_width, img_height = PRESET_SIZES[st.session_state.selected_size]
            st.markdown(
                f"<div style='margin-top:10px;padding:9px 14px;"
                f"background:rgba(56,189,248,0.06);border-radius:12px;"
                f"font-size:13px;color:#38bdf8;font-weight:700;"
                f"border:1px solid rgba(56,189,248,0.18);'>"
                f"✓ {st.session_state.selected_size} — {img_width} × {img_height} px</div>",
                unsafe_allow_html=True
            )

        with size_tab_custom:
            c1, c2 = st.columns(2)
            with c1:
                img_width  = st.number_input("Width (px)",  min_value=256, max_value=1024, value=768, step=16)
            with c2:
                img_height = st.number_input("Height (px)", min_value=256, max_value=1024, value=768, step=16)

        st.markdown("<br>", unsafe_allow_html=True)

        num_sel  = len(st.session_state.selected_themes)
        generate = st.button(
            f"🚀  Generate {num_sel} Image{'s' if num_sel > 1 else ''}",
            width="stretch", type="primary", disabled=(num_sel == 0)
        )

        if st.session_state.results:
            st.markdown(
                "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:24px 0;'>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:22px;font-weight:900;color:#f1f5f9;"
                f"margin-bottom:18px;letter-spacing:-0.5px;'>"
                f"✨ Your Generated Images "
                f"<span style='font-size:14px;font-weight:500;color:#475569;margin-left:10px;'>"
                f"{len(st.session_state.results)} image(s)</span></div>",
                unsafe_allow_html=True
            )
            num_r  = len(st.session_state.results)
            cols_r = st.columns(min(num_r, 3))
            for idx, item in enumerate(st.session_state.results):
                with cols_r[idx % min(num_r, 3)]:
                    st.image(item["image"], width="stretch")
                    st.markdown(
                        f"<div style='text-align:center;margin:8px 0 6px 0;'>"
                        f"<div style='font-size:14px;font-weight:800;color:#f1f5f9;'>"
                        f"<span style='color:#c084fc;'>{item['theme']}</span> · Image {idx+1}</div>"
                        f"<div style='font-size:12px;color:#475569;margin-top:3px;'>"
                        f"🌱 Seed: {item['seed']} · ⏱️ {item['time']}s</div></div>",
                        unsafe_allow_html=True
                    )
                    st.download_button(
                        label=f"⬇️ Download {item['theme']}",
                        data=item["bytes"],
                        file_name=get_download_filename(item["theme"], item["seed"]),
                        mime="image/png",
                        key=f"dl_result_{idx}",
                        width="stretch"
                    )

        if generate:
            if not prompt.strip():
                st.error("❌ Please describe your image first!")
            elif not st.session_state.selected_themes:
                st.error("❌ Please select at least one theme!")
            else:
                st.session_state.results = []
                with st.spinner("🔄 Connecting to FLUX.1-schnell..."):
                    load_flux_pipeline()

                if use_rag:
                    with st.spinner("🗂️ Searching RAG memory..."):
                        rag_context = get_rag_context_string(prompt)
                    if rag_context:
                        st.markdown(
                            f"<div style='background:rgba(52,211,153,0.06);"
                            f"border:1px solid rgba(52,211,153,0.2);border-radius:12px;"
                            f"padding:12px 16px;font-size:13px;color:#6ee7b7;margin-bottom:12px;'>"
                            f"🗂️ <b>RAG context found</b><br>{rag_context}</div>",
                            unsafe_allow_html=True
                        )

                total    = len(st.session_state.selected_themes)
                progress = st.progress(0, text="Starting generation...")

                for idx, theme_name in enumerate(st.session_state.selected_themes):
                    progress.progress(
                        int((idx / total) * 100),
                        text=f"🎨 Generating {theme_name} ({idx+1}/{total})..."
                    )
                    theme_suffix = dict(THEMES).get(theme_name, "")

                    if use_reasoning:
                        with st.spinner(f"🧠 Enhancing prompt for {theme_name}..."):
                            enhanced = enhance_prompt(prompt, theme_suffix)
                        final_prompt = enhanced["enhanced_prompt"]
                    else:
                        suffix       = f", {theme_suffix}" if theme_suffix else ""
                        final_prompt = f"{prompt}{suffix}"

                    t0 = time.time()
                    image, used_seed = generate_image(
                        prompt=final_prompt, width=img_width,
                        height=img_height, quality=quality, seed=seed
                    )
                    elapsed   = round(time.time() - t0, 1)
                    img_path  = save_image(image, final_prompt, used_seed, theme_name)
                    img_bytes = image_to_bytes(image)

                    if use_rag:
                        add_to_rag(prompt, final_prompt, theme_name, img_path)

                    st.session_state.results.append({
                        "theme": theme_name, "image": image,
                        "bytes": img_bytes,  "seed":  used_seed,
                        "time":  elapsed,    "path":  img_path,
                    })
                    st.session_state.last_seed  = used_seed
                    st.session_state.last_time  = elapsed
                    st.session_state.gen_count += 1

                update_gen_count(user["user_id"])
                progress.progress(100, text="✅ All done!")
                st.success(f"✅ Generated {total} image(s) successfully!")
                st.rerun()

    # ── TAB 2: BATCH ──────────────────────────────────────────────────────────
    with tab_batch:
        st.markdown("""
        <div style='padding:22px 0 16px 0;'>
            <div class='page-title'>📦 Batch Generation</div>
            <div class='page-sub'>Generate multiple prompts at once and download as a ZIP file</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<div class='batch-info'>"
            "💡 Enter one prompt per line. Each prompt generates one image.</div>",
            unsafe_allow_html=True
        )

        batch_text = st.text_area(
            "Batch Prompts", height=180,
            placeholder="A red dragon flying over mountains\nA cat astronaut on the moon\nA futuristic city at sunset",
            label_visibility="collapsed"
        )
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            batch_theme = st.selectbox("Theme", [t[0] for t in THEMES], key="batch_theme")
        with col_b2:
            batch_size  = st.selectbox("Size",  list(PRESET_SIZES.keys()), index=2, key="batch_size")

        run_batch = st.button("🚀 Run Batch Generation", width="stretch", type="primary")

        if run_batch and batch_text.strip():
            prompts_list = [p.strip() for p in batch_text.strip().split("\n") if p.strip()]
            bw, bh       = PRESET_SIZES[batch_size]
            theme_suffix = dict(THEMES).get(batch_theme, "")

            with st.spinner("🔄 Loading pipeline..."):
                load_flux_pipeline()

            st.session_state.batch_results = []
            bp = st.progress(0, text="Starting batch...")

            for bi, bp_prompt in enumerate(prompts_list):
                bp.progress(
                    int(bi / len(prompts_list) * 100),
                    text=f"🎨 {bi+1}/{len(prompts_list)}: {bp_prompt[:40]}..."
                )
                full_p         = f"{bp_prompt}, {theme_suffix}" if theme_suffix else bp_prompt
                img, used_seed = generate_image(prompt=full_p, width=bw, height=bh, quality=quality, seed=seed)
                img_bytes      = image_to_bytes(img)
                img_path       = save_image(img, full_p, used_seed, batch_theme)
                st.session_state.batch_results.append({
                    "prompt": bp_prompt, "image": img,
                    "bytes":  img_bytes, "seed":  used_seed, "path": img_path
                })
                st.session_state.gen_count += 1

            update_gen_count(user["user_id"])
            bp.progress(100, text="✅ Batch complete!")
            st.success(f"✅ Generated {len(prompts_list)} images!")
            st.rerun()

        if st.session_state.batch_results:
            st.markdown(
                "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:16px 0;'>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:18px;font-weight:800;color:#f1f5f9;margin-bottom:14px;'>"
                f"📦 Batch Results ({len(st.session_state.batch_results)} images)</div>",
                unsafe_allow_html=True
            )
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                for bi, br in enumerate(st.session_state.batch_results):
                    zf.writestr(f"batch_{bi+1}_seed{br['seed']}.png", br["bytes"])
            zip_buf.seek(0)
            st.download_button(
                "📦 Download All as ZIP", data=zip_buf.getvalue(),
                file_name="batch_images.zip", mime="application/zip",
                width="stretch"
            )
            cols_batch = st.columns(3)
            for bi, br in enumerate(st.session_state.batch_results):
                with cols_batch[bi % 3]:
                    st.image(br["image"], width="stretch")
                    st.caption(f"🌱 Seed {br['seed']} · {br['prompt'][:40]}...")
                    st.download_button(
                        f"⬇️ #{bi+1}", data=br["bytes"],
                        file_name=f"batch_{bi+1}_seed{br['seed']}.png",
                        mime="image/png", key=f"dl_batch_{bi}",
                        width="stretch"
                    )

    # ── TAB 3: SEED BROWSER ───────────────────────────────────────────────────
    with tab_seeds:
        st.markdown("""
        <div style='padding:22px 0 16px 0;'>
            <div class='page-title'>🌱 Seed Browser</div>
            <div class='page-sub'>Explore how different seeds affect the same prompt</div>
        </div>
        """, unsafe_allow_html=True)

        seed_prompt = st.text_input(
            "Prompt for seed exploration",
            placeholder="A magical forest at twilight...", key="seed_prompt"
        )
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            num_seeds  = st.slider("Number of seeds", 2, 6, 4)
        with col_s2:
            seed_theme = st.selectbox("Theme", [t[0] for t in THEMES], key="seed_theme")
        with col_s3:
            seed_size  = st.selectbox("Size",  list(PRESET_SIZES.keys()), index=1, key="seed_size")

        run_seeds = st.button("🌱 Explore Seeds", width="stretch", type="primary")

        if run_seeds and seed_prompt.strip():
            sw, sh       = PRESET_SIZES[seed_size]
            theme_suffix = dict(THEMES).get(seed_theme, "")
            full_p       = f"{seed_prompt}, {theme_suffix}" if theme_suffix else seed_prompt
            seeds        = [random.randint(0, 2**32-1) for _ in range(num_seeds)]

            with st.spinner("🔄 Loading pipeline..."):
                load_flux_pipeline()

            st.session_state.seed_browser_results = []
            sp = st.progress(0, text="Exploring seeds...")

            for si, s_val in enumerate(seeds):
                sp.progress(int(si / num_seeds * 100), text=f"🌱 Seed {s_val} ({si+1}/{num_seeds})...")
                img, used_seed = generate_image(prompt=full_p, width=sw, height=sh, quality="draft", seed=s_val)
                img_bytes      = image_to_bytes(img)
                st.session_state.seed_browser_results.append({
                    "seed": used_seed, "image": img, "bytes": img_bytes
                })

            sp.progress(100, text="✅ Done!")
            st.rerun()

        if st.session_state.seed_browser_results:
            st.markdown(
                "<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:16px 0;'>",
                unsafe_allow_html=True
            )
            cols_seed = st.columns(min(len(st.session_state.seed_browser_results), 3))
            for si, sr in enumerate(st.session_state.seed_browser_results):
                with cols_seed[si % 3]:
                    st.image(sr["image"], width="stretch")
                    st.markdown(
                        f"<div style='text-align:center;font-size:13px;color:#64748b;margin:6px 0;'>"
                        f"🌱 Seed: <b style='color:#c084fc;'>{sr['seed']}</b></div>",
                        unsafe_allow_html=True
                    )
                    col_use, col_dl = st.columns(2)
                    with col_use:
                        if st.button("🔒 Use Seed", key=f"use_seed_{si}", width="stretch"):
                            st.session_state["locked_seed"] = sr["seed"]
                            st.success(f"🔒 Seed {sr['seed']} locked!")
                    with col_dl:
                        st.download_button(
                            "⬇️", data=sr["bytes"],
                            file_name=f"seed_{sr['seed']}.png",
                            mime="image/png", key=f"dl_seed_{si}",
                            width="stretch"
                        )

    # ── TAB 4: GALLERY ────────────────────────────────────────────────────────
    with tab_gallery:
        st.markdown("""
        <div style='padding:22px 0 16px 0;'>
            <div class='page-title'>🖼️ Your Gallery</div>
            <div class='page-sub'>All your generated masterpieces in one place</div>
        </div>
        """, unsafe_allow_html=True)

        history = get_generation_history()
        if not history:
            st.markdown("""
            <div style='text-align:center;padding:70px 0;'>
                <div style='font-size:4rem;opacity:0.15;'>🖼️</div>
                <div style='color:#334155;font-size:16px;margin-top:14px;font-weight:700;'>
                    No images yet — generate your first!
                </div>
                <div style='color:#1e293b;font-size:13px;margin-top:6px;'>
                    Head to the Generate tab to create stunning images
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            cols = st.columns(3)
            for i, item in enumerate(history):
                with cols[i % 3]:
                    img_path = item.get("image_path", "")
                    if img_path and os.path.exists(img_path):
                        img   = Image.open(img_path)
                        theme = item.get("theme", "?")
                        ts    = item.get("timestamp", "")[:10]
                        st.image(img, width="stretch")
                        st.markdown(
                            f"<div style='text-align:center;font-size:12px;color:#475569;"
                            f"margin:5px 0 8px 0;font-weight:600;'>"
                            f"{THEME_ICONS.get(theme,'⚪')} {theme} · {ts}</div>",
                            unsafe_allow_html=True
                        )
                        with open(img_path, "rb") as f:
                            st.download_button(
                                "⬇️ Download", data=f.read(),
                                file_name=os.path.basename(img_path),
                                mime="image/png", key=f"dl_gal_{i}",
                                width="stretch"
                            )
                        show_prompt = st.toggle(
                            "📋 View Prompt", value=False, key=f"show_prompt_{i}"
                        )
                        if show_prompt:
                            st.write(item.get("original_prompt", "N/A"))

    # ── TAB 5: ABOUT ──────────────────────────────────────────────────────────
    with tab_about:
        st.markdown("""
        <div style='padding:22px 0 16px 0;'>
            <div class='page-title'>ℹ️ About AI Image Studio</div>
            <div class='page-sub'>Built with cutting-edge AI models and modern web technologies</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color:#f1f5f9;margin-bottom:18px;font-size:16px;font-weight:800;'>🏗️ Tech Stack</h4>
                <div style='display:flex;flex-direction:column;gap:14px;'>
                    <div style='border-left:3px solid #c084fc;padding-left:14px;'>
                        <div style='font-size:14px;font-weight:700;color:#c084fc;'>FLUX.1-schnell</div>
                        <div style='font-size:12.5px;color:#64748b;margin-top:2px;'>HuggingFace API · 12B params · Free tier</div>
                    </div>
                    <div style='border-left:3px solid #60a5fa;padding-left:14px;'>
                        <div style='font-size:14px;font-weight:700;color:#60a5fa;'>Mistral 7B (Ollama)</div>
                        <div style='font-size:12.5px;color:#64748b;margin-top:2px;'>Local LLM · Prompt enhancement</div>
                    </div>
                    <div style='border-left:3px solid #34d399;padding-left:14px;'>
                        <div style='font-size:14px;font-weight:700;color:#34d399;'>FAISS + MiniLM</div>
                        <div style='font-size:12.5px;color:#64748b;margin-top:2px;'>Local vector DB · RAG memory</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color:#f1f5f9;margin-bottom:18px;font-size:16px;font-weight:800;'>🚀 Features</h4>
                <div style='display:flex;flex-direction:column;gap:10px;font-size:13px;color:#64748b;'>
                    <div>🎨 Text-to-Image generation with 12+ themes</div>
                    <div>📦 Batch generation with ZIP download</div>
                    <div>🌱 Seed Browser for variation exploration</div>
                    <div>🧠 Mistral AI prompt enhancement</div>
                    <div>🗂️ RAG Memory for context-aware generation</div>
                    <div>🖼️ Gallery with full history</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")


# ═════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    show_auth_page()
else:
    show_main_app()
