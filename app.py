import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import feedparser
from openai import OpenAI
from datetime import datetime

# Sidkonfiguration
st.set_page_config(
    page_title="SWINGKINGS",
    page_icon="👑",
    layout="wide"
)

# Inspirerande mörk bakgrund och styling
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #06090f 0%, #0b0e14 50%, #111827 100%) !important;
        color: #e0e6ed !important;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #1f2937 !important;
    }
    .logo-header-box {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
        border: 2px solid #38bdf8;
        box-shadow: 0 0 30px rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 25px 30px;
        margin-bottom: 25px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .logo-title {
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .logo-sub {
        color: #94a3b8;
        font-size: 0.95rem;
        letter-spacing: 2.5px;
        margin-top: 8px;
        text-transform: uppercase;
    }
    .stock-card {
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 10px;
        backdrop-filter: blur(5px);
    }
    .gazelle-box {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 2px solid #eab308;
        box-shadow: 0 0 25px rgba(234, 179, 8, 0.25);
        border-radius: 14px;
        padding: 22px;
        margin-top: 35px;
        margin-bottom: 20px;
    }
    .news-box {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #38bdf8;
        border-radius: 14px;
        padding: 22px;
        margin-top: 30px;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }
</style>
""", unsafe_allow_html=True)

# Dagens datum
today_str = datetime.now().strftime("%Y-%m-%d")

# Inramad SWINGKINGS Logotyp
st.markdown(f"""
    <div class="logo-header-box">
        <h1 class="logo-title">👑 SWINGKINGS</h1>
        <div class="logo-sub">DAGLIG QUANT ENGINE // DATUM: {today_str}</div>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, S
