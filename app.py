import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import altair as alt
from datetime import datetime

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0", page_icon="👑", layout="wide")

CSS_STYLE = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #05070b, #0a0e17, #0f172a) !important;
    color: #e2e8f0 !important;
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background-color: #090d14 !important;
    border-right: 1px solid #1e293b !important;
}
.logo-header-box {
    background: rgba(15, 23, 42, 0.95);
    border: 2px solid #38bdf8;
    box-shadow: 0 0 35px rgba(56, 189, 248, 0.25);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 25px;
    text-align: center;
}
.logo-title {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: 3px;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.logo-sub {
    color: #94a3b8;
    font-size: 0.88rem;
    letter-spacing: 2px;
    margin-top: 8px;
    text-transform: uppercase;
}
.stock-card {
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
}
.argon-badge {
    background: linear-gradient(90deg, #0284c7, #2563eb);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    float: right;
}
.bear-badge {
    background: linear-gradient(90deg, #dc2626, #991b1b);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    float: right;
}
.gazelle-badge {
    background: linear-gradient(90deg, #eab308, #ca8a04);
    color: #000000;
    padding: 4px 12px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 800;
    float: right;
}
.report-box {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid #38bdf8;
    border-left: 5px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 12px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.bear-report-box {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid #ef4444;
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 12px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.gazelle-box {
    background: rgba(15, 23, 42, 0.96);
    border: 2px solid #eab308;
    box-shadow: 0 0 25px rgba(234, 179, 8, 0.25);
    border-radius: 14px;
    padding: 22px;
    margin-top: 30px;
    margin-bottom: 15px;
    line-height: 1.6;
}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d")

st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
portfolio_sek = st.sidebar.number_input("Portföljstorlek:", 10000, 10000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)

DEFAULT_TICKERS = "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=120)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(
    "<div class='logo-header-box'>"
    f"<h1 class='logo-title'>👑 SWINGKINGS // ARGON v2.0</h1>"
    f"<div class='logo-sub'>ATR-DYNAMIC LEVELS // VCP SQUEEZE // RS-ALPHA SCANNER // {today_str}</div>"
    "</div>",
    unsafe_allow_html=True
)

@st.cache_data(ttl=900)
def fetch_argon_v2_data(tickers):
    omx_5d, spx_5d = 0.0, 0.0
    try:
        omx = yf.Ticker("^OMX").history(period="1mo")
        if len(omx) >= 6:
            omx_5d = ((float(omx["Close"].iloc[-1]) - float(omx["Close"].iloc[-6])) / float(omx["Close"].iloc[-6])) * 100
    except Exception:
        pass
    try:
        spx = yf.Ticker("^GSPC").history(period="1mo")
        if len(spx) >= 6:
            spx_5d = ((float(spx["Close"].iloc[-1]) - float(spx["Close"].iloc[-6])) / float(spx["Close"].iloc[-6])) * 100
    except Exception:
        pass

    results = []
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            if df.empty or len(df) < 20:
                continue
            close, high, low, vol = df["Close"], df["High"], df["Low"], df["Volume"]
            c_now, c_prev, y_high = float(close.iloc[-1]), float(close.iloc[-2]), float(high.iloc[-2])
            pct_1d = ((c_now - c_prev) / c_prev) * 100
            c_5d = float(close.iloc[-6]) if len(close) >= 6 else c_prev
            pct_5d = ((c_now - c_5d) / c_5d) * 100

            is_se = ticker.endswith(".ST")
            valuta = "SEK" if is_se else "USD"
            rs_alpha = pct_5d - (omx_5d if is_se else spx_5d)

            rsi_s = ta.momentum.rsi(close=close, window=14)
            rsi_v = float(rsi_s.iloc[-1]) if not pd.isna(rsi_s.iloc[-1]) else 50.0
            ema10 = float(close.ewm(span=10, adjust=False).mean().iloc[-1])
            sma50 = float(close.tail(50).mean()) if len(close) >= 50 else float(close.tail(20).mean())
            high_20 = float(high.tail(20).max())

            tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
            atr_14 = float
