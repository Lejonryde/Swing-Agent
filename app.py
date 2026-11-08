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
        padding: 16px;
        margin-bottom: 15px;
        backdrop-filter: blur(5px);
    }
    .report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #38bdf8;
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.95rem;
    }
    .bear-report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.95rem;
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

# Sidebar - definieras först så variablerna finns tillgängliga direkt
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password", key="openai_api_key_field")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, "
    "TELIA.ST, SINCH.ST, NVDA, TSLA, AMD, PLTR"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Inramad SWINGKINGS Logotyp
st.markdown(
    f'<div class="logo-header-box">'
    f'<h1 class="logo-title">👑 SWINGKINGS</h1>'
    f'<div class="logo-sub">DAGLIG QUANT ENGINE // DATUM: {today_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Hämtar marknadsdata
market_data = []
for ticker in tickers_list:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
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

# Sortering: Bull vs Bear
bull_candidates = sorted([d for d in market_data if d['pct'] >= 0 or d['rsi'] > 50], key=lambda x: x['pct'], reverse=True)
bear_candidates = sorted([d for d in market_data if d['pct'] < 0 or d['rsi'] < 45], key=lambda x: x['pct'])

if not bull_candidates: 
    bull_candidates = market_data[:3]
if not bear_candidates: 
    bear_candidates = market_data[-3:]

top_tickers = set([item['ticker'] for item in bull_candidates[:3]] + [item['ticker'] for item in bear_candidates[:3]])

remaining_candidates = [d for d in market_data if d['ticker'] not in top_tickers]
if not remaining_candidates:
    remaining_candidates = market_data

gazelle = max(remaining_candidates, key=lambda x: x['volatility'])

# Delad skärm för Bull och Bear
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #38bdf8;'>KÖP & BREAKOUTS (TOPP 3)</h4>", unsafe_allow_html=True)
    
    for item in bull_candidates[:3]:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        entry_price = item['close'] * 0.99
        target_price = item['close'] * 1.05
        stop_loss = item['close'] * 0.96
        
        card_html = (
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #38bdf8;">⚡ {item["ticker"]}</h3>'
            f'<p style="margin: 4px 0; font-size: 1rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Högsta: {item["high_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item['history'], height=120)
        
        report_html = (
            f'<div class="report-box">'
            f'<b>📊 Kvantrapport & Nivåer ({item["ticker"]}):</b><br>'
            f'• <b>Entry:</b> {entry_price:.2f} {item["valuta"]}<br>'
            f'• <b>Target:</b> <span style="color: #22c55e;">{target_price:.2f} {item["valuta"]} (+5%)</span><br>'
            f'• <b>Stop-Loss:</b> <span style="color: #ef4444;">{stop_loss:.2f} {item["valuta"]} (-4%)</span><br>'
            f'• <i>Status: Bullish momentum med starkt stöd vid 20-dagarslinjen.</i>'
            f'</div>'
        )
        st.markdown(report_html, unsafe_allow_html=True)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171;'>SÄLJ & EXITS (TOPP 3)</h4>", unsafe_allow_html=True)
    
    for item in bear_candidates[:3]:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        short_entry = item['close'] * 1.01
        short_target = item['close'] * 0.95
        short_stop = item['close'] * 1.03
        
        card_html = (
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #f87171;">💀 {item["ticker"]}</h3>'
            f'<p style="margin: 4px 0; font-size: 1rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Lägsta: {item["low_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item['history'], height=120)
        
        bear_report_html = (
            f'<div class="bear-report-box">'
            f'<b>📊 Riskrapport & Exitnivåer ({item["ticker"]}):</b><br>'
            f'• <b>Short Entry:</b> {short_entry:.2f} {item["valuta"]}<br>'
            f'• <b>Target:</b> <span style="color: #22c55e;">{short_target:.2f} {item["valuta"]} (-5%)</span><br>'
            f'• <b>Stop-Loss:</b> <span style="color: #ef4444;">{short_stop:.2f} {item["valuta"]} (+3%)</span><br>'
            f'• <i>Status: Nedåtgående press med ökad rasrisk under nyckelnivåer.</i>'
            f'</div>'
        )
        st.markdown(bear_report_html, unsafe_allow_html=True)

# ==================== VECKANS GASELL (HÖGVOLATIL OUTSIDER) ====================
gazelle_pct_color = "#22c55e" if gazelle['pct'] >= 0 else "#ef4444"
g_entry = gazelle['close'] * 0.98
g_target = gazelle['close'] * 1.10
g_stop = gazelle['close'] * 0.93

st.markdown("---")
gazelle_html = (
    f'<div class="gazelle-box">'
    f'<h2 style="color: #eab308; margin: 0;">🔥 VECKANS GASELL (HÖGVOLATIL OUTSIDER)</h2>'
    f'<h4 style="color: #38bdf8; margin-top: 5px;">VALD OUTSIDER: {gazelle["ticker"]} (Volatilitet: {gazelle["volatility"]:.1f}%)</h4>'
    f'<p style="font-size: 1.1rem; margin-bottom: 10px;">'
    f'<b>Slutkurs:</b> {gazelle["close"]:.2f} {gazelle["valuta"]} '
    f'<span style="color: {gazelle_pct_color}; font-weight: bold;">({gazelle["pct"]:+.2f}%)</span> | '
    f'<b>RSI:</b> {gazelle["rsi"]:.1f} | '
    f'<b>20d Högsta:</b> {gazelle["high_20"]:.2f} {gazelle["valuta"]} | '
    f'<b>20d Lägsta:</b> {gazelle["low_20"]:.2f} {gazelle["valuta"]}'
    f'</p>'
    f'<hr style="border-color: #eab308; opacity: 0.3;">'
    f'<b>📊 Gasell-Rapport & Nivåer:</b><br>'
    f'• <b>Entry:</b> {g_entry:.2f} {gazelle["valuta"]}<br>'
    f'• <b>Target:</b> <span style="color: #22c55e;">{g_target:.2f} {gazelle["valuta"]} (+10%)</span><br>'
    f'• <b>Stop-Loss:</b> <span style="color: #ef4444;">{g_stop:.2f} {gazelle["valuta"]} (-7%)</span><br>'
    f'• <i>Status: Hög volatilitet och brett prisintervall ger stor potential för snabba rörelser.</i>'
    f'</div>'
)
st.markdown(gazelle_html, unsafe_allow_html=True)
st.line_chart(gazelle['history'], height=160)

# ==================== DAGENS EKONOMIRUBRIKER & MAKRO (AUTOMATISK) ====================
st.markdown(
    '<div class="news-box">'
    '<h3 style="color: #38bdf8; margin-top: 0;">📰 DAGENS EKONOMIRUBRIKER & MAKRO</h3>',
    unsafe_allow_html=True
)

if not openai_key:
    st.warning("⚠️ Ange din OpenAI API-nyckel i sidopanelen för att läsa in automatiska makro- och nyhetsrubriker.")
else:
    try:
        with st.spinner("Laddar dagsfärska makro- och nyhetsrubriker..."):
            client = OpenAI(api_key=openai_key)
            news_resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Du är en finansiell nyhetsanalytiker. Dagens datum är idag ({today_str}). Skriv dagsaktuella tunga ekonomirubriker och korta sammanfattningar för börsen och makroläget just nu på svenska med emojis."},
                    {"role": "user", "content": f"Ge mig de viktigaste ekonomirubrikerna och marknadsläget för idag {today_str}."}
                ]
            )
            st.markdown(news_resp.choices[0].message.content)
    except Exception as e:
        st.error(f"Kunde inte hämta nyheter: {e}")

st.markdown('</div>', unsafe_allow_html=True)
