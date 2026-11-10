import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime

# ==================== SIDKONFIGURATION ====================
st.set_page_config(
    page_title="SWINGKINGS // ARGON ENGINE",
    page_icon="👑",
    layout="wide"
)

# ==================== MÖRK NEONGLÖDANDE STYLING ====================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #05070b 0%, #0a0e17 50%, #0f172a 100%) !important;
        color: #e2e8f0 !important;
        background-attachment: fixed;
    }
    [data-testid="stSidebar"] {
        background-color: #090d14 !important;
        border-right: 1px solid #1e293b !important;
    }
    .logo-header-box {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(23, 37, 84, 0.85) 100%);
        border: 2px solid #38bdf8;
        box-shadow: 0 0 35px rgba(56, 189, 248, 0.25);
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 25px;
        text-align: center;
        backdrop-filter: blur(12px);
    }
    .logo-title {
        font-size: 3.1rem;
        font-weight: 900;
        letter-spacing: 4px;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .logo-sub {
        color: #94a3b8;
        font-size: 0.92rem;
        letter-spacing: 2.5px;
        margin-top: 8px;
        text-transform: uppercase;
        font-weight: 600;
    }
    .stock-card {
        background: rgba(17, 24, 39, 0.88);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        backdrop-filter: blur(6px);
    }
    .argon-badge {
        background: linear-gradient(90deg, #0284c7, #2563eb);
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        float: right;
    }
    .bear-badge {
        background: linear-gradient(90deg, #dc2626, #991b1b);
        color: #ffffff;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 700;
        float: right;
    }
    .report-box {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #38bdf8;
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 6px;
        margin-bottom: 22px;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .bear-report-box {
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 6px;
        margin-bottom: 22px;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .gazelle-box {
        background: linear-gradient(135deg, rgba(234, 179, 8, 0.14) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 2px solid #eab308;
        box-shadow: 0 0 30px rgba(234, 179, 8, 0.25);
        border-radius: 14px;
        padding: 24px;
        margin-top: 30px;
        margin-bottom: 20px;
    }
    .news-box {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid #38bdf8;
        border-radius: 14px;
        padding: 24px;
        margin-top: 35px;
        margin-bottom: 30px;
        backdrop-filter: blur(6px);
    }
</style>
""", unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d")

# ==================== SIDEBAR & UTÖKAT GULDKORNS-UNIVERSUM ====================
st.sidebar.header("🕹️ ARGON CONTROL PANEL")
st.sidebar.subheader("💎 GULDKORNS-UNIVERSUM")

default_universe = (
    "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, "
    "ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, "
    "BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, "
    "SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, "
    "INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, "
    "PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
)

custom_tickers = st.sidebar.text_area("Aktiva tickers (32 st förvalda):", default_universe, height=180)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# ==================== LOGOTYP & HEADER ====================
header_html = (
    '<div class="logo-header-box">'
    '<h1 class="logo-title">👑 SWINGKINGS // ARGON</h1>'
    f'<div class="logo-sub">MULTI-FACTOR QUANT & GOLDMINE SCANNER (10+10 AKTIER // 7-10 DAGAR // MÅL 8-10%) // {today_str}</div>'
    '</div>'
)
st.markdown(header_html, unsafe_allow_html=True)

# ==================== SEKTOR- & FUNDAMENTAL DATABAS ====================
SECTOR_PROFILES = {
    "VOLV-B.ST": (" Tung Verkstad & Transport", "Urstark balansräkning, hög direktavkastning och stark prisdisciplin i konjunkturcykeln."),
    "SAAB-B.ST": ("Försvar & Säkerhet", "Strukturell supercykel driven av ökande europeiska försvarsanslag och rekordstor orderbok."),
    "MYCR.ST": ("Halvledarutrustning & Tech", "Global monopolställning inom maskritare för bildskärmar och halvledare med extrema bruttomarginaler."),
    "BONE.ST": ("Medtech & Ortopedi", "Explosiv försäljningstillväxt i USA för syntetiska bengraft med skyllhöga bruttomarginaler."),
    "CAMX.ST": ("Biotech & Läkemedel", "Stark kommersialisering av depåläkemedel och solida kassaflöden i en ocyklisk tillväxtfas."),
    "ATCO-A.ST": ("Verkstad & Vakuumteknik", "Kvalitetsledare inom industriell automation och halvledarvakuum som institutioner alltid ackumulerar i dippar."),
    "ABB.ST": ("Elektrifiering & Automation", "Gynnas direkt av globala elnätsinvesteringar, AI-datacenter och industriell robotisering."),
    "SAND.ST": ("Gruvutrustning & Verkstad", "Hög exponering mot stigande metallpriser och global gruvautomation med starkt eftermarknadsflöde."),
    "HEXA-B.ST": ("Mätteknik & Mjukvara", "Hög andel återkommande mjukvaruintäkter och positionerad för industriell digitalisering."),
    "EVOL.ST": ("iGaming & Tech", "Marknadsdominant med över 60% EBITDA-marginal, starka kassaflöden och aggressiva aktieåterköp."),
    "BOL.ST": ("Gruvor & Basmetaller", "Direkt hävstång mot koppar-, zink- och guldpriser i elektrifieringsvågen."),
    "SSAB-B.ST": ("Specialstål & Råvaror", "Högcyklisk stålproducent med stark kassa som rör sig kraftigt vid skiften i europeisk industrikonjunktur."),
    "FNOX.ST": ("SaaS & Finansiell Mjukvara", "Sveriges starkaste SaaS-ekosystem med prishöjningskraft och skalbara marginaler."),
    "NIBE-B.ST": ("Värmepumpar & Klimatteknik", "Långsiktig vinnare på europeisk energiomställning som erbjuder kraftiga motreaktioner efter lagerkorrigeringar."),
    "EMBRAC-B.ST": ("Gaming & Underhållning", "Högvolatil turnaround-kandidat där avknoppningar och spelsläpp driver snabba kortsiktiga flöden."),
    "SINCH.ST": ("Molnkommunikation", "Räntekänslig tech-outsider med hög beta som reagerar explosivt vid lägre marknadsräntor."),
    "SBB-B.ST": ("Fastigheter", "Skuldtyngt fastighetsbolag med extrem räntekänslighet och volatila obligationsflöden."),
    "ERIC-B.ST": ("Telekom & 5G", "Cyklisk nätverksjätte där nordamerikanska operatörsinvesteringar styr marginaltrenden."),
    "HM-B.ST": ("Detaljhandel & Konsument", "Starkt beroende av bruttomarginal, fraktpriser och konsumenternas köpkraft."),
    "GETI-B.ST": ("Medicinteknik", "Vär
