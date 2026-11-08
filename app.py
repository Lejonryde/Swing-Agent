import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="SWING KING // TERMINAL",
    page_icon="🦁",
    layout="wide"
)

# ULTRA-MODERN DARK TERMINAL CSS
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
    
    /* BULL ZONE - NEON BLUE */
    .bull-container {
        background: linear-gradient(180deg, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 2px solid #0284c7;
        box-shadow: 0 0 20px rgba(2, 132, 199, 0.3);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    /* BEAR ZONE - NEON RED */
    .bear-container {
        background: linear-gradient(180deg, rgba(239, 68, 68, 0.15) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 2px solid #dc2626;
        box-shadow: 0 0 20px rgba(220, 38, 38, 0.3);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
    }
    
    .brand-header {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #38bdf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }
    
    .badge-bull {
        background-color: #0284c7;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }

    .badge-bear {
        background-color: #dc2626;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    
    /* Custom style for Streamlit buttons */
    .stButton>button {
        width: 100%;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        height: 48px !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        transition: all 0.2s ease-in-out !important;
    }
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown('<div class="brand-header">🦁 SWING KING TERMINAL</div>', unsafe_allow_html=True)
st.caption("LEJONRYDE CAPITAL QUANT ENGINE // REALTIME BREAKOUT & EXIT PROTOCOL")
st.markdown("---")

# SIDEBAR
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 TARGET WATCHLIST")
custom_tickers = st.sidebar.text_area(
    "Tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST, NVDA, TSLA, AMD, PLTR"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# MAIN SCREEN SPLIT
col_buy, col_sell = st.columns(2, gap="large")

# ==================== LEFT: BULL DIVISION (BLUE) ====================
with col_buy:
    st.markdown("""
        <div class="bull-container">
            <span class="badge-bull">BULL DIVISION</span>
            <h2 style="color: #38bdf8; margin-top: 10px; font-weight: 800;">⚡ DAGENS KÖP & BREAKOUTS</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">Hitta momentum, volymutbrott och nästa kursraket.</p>
        </div>
    """, unsafe_allow_html=True)
    
    run_buy = st.button("🔥 UTELÖS KÖPATTIK", key="btn_buy")
    
    if run_buy:
        if not openai_key:
            st.error("❌ OpenAI API Key saknas i Secrets/Sidebar!")
        else:
            stock_data_list = []
            with st.spinner("Skannar orderdjup & momentum..."):
                for ticker in tickers_list:
                    try:
                        stock = yf.Ticker(ticker)
                        df = stock.history(period
                        
