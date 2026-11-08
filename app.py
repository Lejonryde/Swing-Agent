import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="SWING KING // TERMINAL",
    page_icon="👑",
    layout="wide"
)

# ULTRA-MODERN DARK BLOOMBERG/TRADING TERMINAL CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0b0e14 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #e0e6ed !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #121824 !important;
        border-right: 1px solid #1e293b !important;
    }

    .brand-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }

    .bull-box {
        background: linear-gradient(180deg, rgba(0, 123, 255, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 2px solid #0284c7;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .bear-box {
        background: linear-gradient(180deg, rgba(220, 53, 69, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 2px solid #dc2626;
        box-shadow: 0 0 15px rgba(220, 38, 38, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Huvudrubrik
st.markdown('<div class="brand-title">👑 SWING KING</div>', unsafe_allow_html=True)
st.caption("LEJONRYDE CAPITAL QUANT ENGINE // FREDAGSRAPPORT & BREAKOUT PROTOCOL")
st.markdown("---")

# Sidebar
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Delad skärm
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    st.markdown("""
        <div class="bull-box">
            <h2 style='color: #38bdf8; margin: 0
