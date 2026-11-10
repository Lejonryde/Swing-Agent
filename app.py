import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="SWINGKINGS",
    page_icon="👑",
    layout="wide"
)

# Mörk neonglödande styling
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
        margin-bottom: 12px;
        backdrop-filter: blur(5px);
    }
    .report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #38bdf8;
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 18px;
        font-size: 0.9rem;
    }
    .bear-report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 18px;
        font-size: 0.9rem;
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
        margin-top: 35px;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }
</style>
""", unsafe_allow_html=True)

# Dagens datum
today_str = datetime.now().strftime("%Y-%m-%d")

# Säkert hämtande av OpenAI API-nyckel från Streamlit Secrets
openai_key = ""
try:
    if "OPENAI_API_KEY" in st.secrets:
        openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

if not openai_key:
    openai_key = os.environ.get("OPENAI_API_KEY", "")

# Sidebar - Utökad bevakningslista för att täcka 10+10 aktier
st.sidebar.header("🕹️ CONTROL PANEL")
st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST, "
    "EVOL.ST, BOL.ST, NDA-SE.ST, GETIB.ST, HEXA-B.ST, ATCO-A.ST, "
    "SAND.ST, ABB.ST, INVE-B.ST, HM-B.ST, SEB-A.ST, SHB-A.ST, "
    "NVDA, TSLA, AMD, PLTR, AAPL, MSFT"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Inramad SWINGKINGS Logotyp
st.markdown(
    f'<div class="logo-header-box">'
    f'<h1 class="logo-title">👑 SWINGKINGS</h1>'
    f'<div class="logo-sub">SWINGTRADE ENGINE (10+10 AKTIER // 7-10 DAGAR) // DATUM: {today_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Hämtar marknadsdata
market_data = []
for ticker in tickers_list:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1.5mo")
        if df.empty or len(df) < 5:
            continue
        close_ser = df['Close']
        latest_close = close_ser.iloc[-1]
        prev_close = close_ser.iloc[-2]
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        valuta = "SEK" if ticker.endswith(".ST") else "USD"
        rsi_val = ta.momentum.rsi(close=close_ser, window=14).iloc[-1]
        high_20 = df['High'].max()
        low_20 = df['Low'].min()
        
        volatility_spread = ((high_20 - low_20) / low_20) * 100
        
        market_data.append({
            "ticker": ticker,
            "close": latest_close,
            "pct": pct_change,
            "valuta": valuta,
            "rsi": rsi_val,
            "high_20": high_20,
            "low_20": low_20,
            "volatility": volatility_spread,
            "history": close_ser.tail(10)
        })
    except Exception:
        continue

if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas. Kontrollera dina tickers.")
    st.stop()

# ==================== STRIKT ÖMSESIDIG uteslutning (MUTUAL EXCLUSIVITY) ====================
# Sortera alla efter procentuell förändring / momentum
sorted_market = sorted(market_data, key=lambda x: x['pct'], reverse=True)

# Top 10 för Bull-divisionen (starka bolag / dip-swings)
bull_candidates = sorted_market[:10]
bull_tickers = {item['ticker'] for item in bull_candidates}

# Resterande sorteras för Bear-divisionen (svaga flöden / rasrisker), ta upp till 10
remaining_for_bear = [d for d in market_data if d['ticker'] not in bull_tickers]
bear_candidates = sorted(remaining_for_bear, key=lambda x: x['pct'])[:10]
bear_tickers = {item['ticker'] for item in bear_candidates}

# Välj gasell bland kvarvarande aktier som inte är med i Bull eller Bear
leftovers = [d for d in market_data if d['ticker'] not in bull_tickers and d['ticker'] not in bear_tickers]
if not leftovers:
    leftovers = market_data
gazelle = max(leftovers, key=lambda x: x['volatility'])

# Delad skärm för Bull och Bear
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (BULL DIVISION - 10 ST) ====================
with col_buy:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #38bdf8;'>STÄRKA BOLAG & KONTROLLERADE DIP-SWINGS</h4>", unsafe_allow_html=True)
    
    for item in bull_candidates:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        entry_price = item['close'] * 0.985 # Optimerad dipp-entry (-1.5%)
        target_price = item['close'] * 1.085 # Mål +8.5% avkastning på 7-10 dagar
        stop_loss = item['close'] * 0.955   # Stram riskhantering (-4.5%)
        
        card_html = (
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #38bdf8;">⚡ {item["ticker"]}</h3>'
            f'<p style="margin: 4px 0; font-size: 0.95rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Högsta: {item["high_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item['history'], height=100)
        
        report_html = (
            f'<div class="report-box">'
            f'<b>📊 7-10 Dagars Swing-Setup ({item["ticker"]}):</b><br>'
            f'• <b>Entry:</b> {entry_price:.2f} {item["valuta"]} (Avvaktar dipp)<br>'
            f'• <b>Target (+8.5%):</b> <span style="color: #22c55e;">{target_price:.2f} {item["valuta"]}</span><br>'
            f'• <b>Stop-Loss (-4.5%):</b> <span style="color: #ef4444;">{stop_loss:.2f} {item["valuta"]}</span><br>'
            f'• <i>Strategi: Stark cyklisk struktur, optimerad för kortsiktig studs.</i>'
            f'</div>'
        )
        st.markdown(report_html, unsafe_allow_html=True)


# ==================== HÖGER HALVA: RÖD (BEAR DIVISION - 10 ST) ====================
with col_sell:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171;'>SVAGA FLÖDESBOLAG & RASRISKER</h4>", unsafe_allow_html=True)
    
    for item in bear_candidates:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        short_entry = item['close'] * 1.01
        short_target = item['close'] * 0.92
        short_stop = item['close'] * 1.035
        
        card_html = (
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #f87171;">💀 {item["ticker"]}</h3>'
            f'<p style="margin: 4px 0; font-size: 0.95rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Lägsta: {item["low_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item['history'], height=100)
        
        bear_report_html = (
            f'<div class="bear-report-box">'
            f'<b>📊 Riskrapport & Short-Nivåer ({item["ticker"]}):</b><br>'
            f'• <b>Short Entry:</b> {short_entry:.2f} {item["valuta"]}<br>'
            f'• <b>Target (-8%):</b> <span style="color: #22c55e;">{short_target:.2f} {item["valuta"]}</span><br>'
            f'• <b>Stop-Loss:</b> <span style="color: #ef4444;">{short_stop:.2f} {item["valuta"]}</span><br
