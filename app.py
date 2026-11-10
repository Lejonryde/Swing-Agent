import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
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
.report-box {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid #38bdf8;
    border-left: 5px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 22px;
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
    margin-bottom: 22px;
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
    margin-bottom: 20px;
}
.news-box {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid #38bdf8;
    border-radius: 14px;
    padding: 22px;
    margin-top: 35px;
    margin-bottom: 30px;
}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d")

st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
st.sidebar.subheader("💰 RISK & POSITIONSSTORLEK")
portfolio_sek = st.sidebar.number_input("Portföljstorlek:", 10000, 10000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)
max_risk_cash = portfolio_sek * (risk_pct / 100.0)
st.sidebar.caption(f"Max förlust vid Stop-Loss: **{max_risk_cash:.0f}** valutaenheter")

st.sidebar.subheader("💎 GULDKORNS-UNIVERSUM")
DEFAULT_TICKERS = (
    "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, "
    "ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, "
    "BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, "
    "SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, "
    "INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, "
    "PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
)
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=150)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(f"""
<div class="logo-header-box">
    <h1 class="logo-title">👑 SWINGKINGS // ARGON v2.0</h1>
    <div class="logo-sub">ATR-DYNAMIC LEVELS // VCP SQUEEZE // RS-ALPHA SCANNER // {today_str}</div>
</div>
""", unsafe_allow_html=True)

PROFILES = {
    "VOLV-B.ST": "<b>Tung Verkstad:</b> Urstark balansräkning, hög direktavkastning och stark prisdisciplin.",
    "SAAB-B.ST": "<b>Försvar & Säkerhet:</b> Strukturell supercykel driven av ökande försvarsanslag och rekordorderbok.",
    "MYCR.ST": "<b>Halvledarutrustning:</b> Global monopolställning inom maskritare med extrema bruttomarginaler.",
    "BONE.ST": "<b>Medtech & Ortopedi:</b> Explosiv försäljningstillväxt i USA med skyhöga bruttomarginaler.",
    "CAMX.ST": "<b>
