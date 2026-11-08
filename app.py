import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
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
st.markdown(
    f'<div class="logo-header-box">'
    f'<h1 class="logo-title">👑 SWINGKINGS</h1>'
    f'<div class="logo-sub">DAGLIG QUANT ENGINE // DATUM: {today_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, "
    "TELIA.ST, SINCH.ST, NVDA, TSLA, AMD, PLTR"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

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
    st.write("Dagens starkaste köpkandidater:")
    
    for item in bull_candidates[:3]:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        st.markdown(
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #38bdf8;">⚡ {item["ticker"]}</h3>'
            f'<p style="margin: 2px 0; font-size: 1rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Högsta: {item["high_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        st.line_chart(item['history'], height=120)

    run_buy = st.button("🚀 KÖP-ANALYS (AI)", use_container_width=True, key="btn_buy")
    
    if run_buy:
        if not openai_key or not openai_key.startswith("sk-"):
            st.warning("⚠️ Vänligen ange en giltig OpenAI API-nyckel i sidopanelen för att köra AI-analysen.")
        else:
            try:
                with st.spinner("AI vaskar fram dagens bästa köpcasen..."):
                    market_text = ",\n".join([f"{i['ticker']}: {i['close']} {i['valuta']} ({i['pct']}%)" for i in bull_candidates[:3]])
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är elit-trader. Analysera stenhårt på svenska med emojis, entries och stop-loss."},
                            {"role": "user", "content": f"Analysera köpcasen:\n{market_text}"}
                        ]
                    )
                    st.success("AI-RAPPORT KLAR")
                    st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Kunde inte nå OpenAI: {e}")


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171;'>SÄLJ & EXITS (TOPP 3)</h4>", unsafe_allow_html=True)
    st.write("Dagens säljkandidater och rasrisker:")
    
    for item in bear_candidates[:3]:
        pct_color = "#22c55e" if item['pct'] >= 0 else "#ef4444"
        st.markdown(
            f'<div class="stock-card">'
            f'<div><h3 style="margin: 0; color: #f87171;">💀 {item["ticker"]}</h3>'
            f'<p style="margin: 2px 0; font-size: 1rem;">'
            f'<b>{item["close"]:.2f} {item["valuta"]}</b> '
            f'<span style="color: {pct_color}; font-weight: bold;">({item["pct"]:+.2f}%)</span> '
            f'| RSI: <b>{item["rsi"]:.1f}</b></p>'
            f'<small style="color: #94a3b8;">20d Lägsta: {item["low_20"]:.2f} {item["valuta"]}</small>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        st.line_chart(item['history'], height=120)

    run_sell = st.button("🛑 SÄLJ-ANALYS (AI)", use_container_width=True, key="btn_sell")
    
    if run_sell:
        if not openai_key or not openai_key.startswith("sk-"):
            st.warning("⚠️ Vänligen ange en giltig OpenAI API-nyckel i sidopanelen för att köra AI-analysen.")
        else:
            try:
                with st.spinner("AI analyserar dagens säljsignaler..."):
                    market_text = ",\n".join([f"{i['ticker']}: {i['close']} {i['valuta']} ({i['pct']}%)" for i in bear_candidates[:3]])
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är skoningslös riskmanager. Peka ut rasrisker på svenska med emojis."},
                            {"role": "user", "content": f"Analysera säljsignaler:\n{market_text}"}
                        ]
                    )
                    st.success("AI-RAPPORT KLAR")
                    st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Kunde inte nå OpenAI: {e}")

# ==================== VECKANS GASELL (HÖGVOLATIL OUTSIDER) ====================
gazelle_pct_color = "#22c55e" if gazelle['pct'] >= 0 else "#ef4444"
st.markdown("---")
st.markdown(
    f'<div class="gazelle-box">'
    f'<h2 style="color: #eab308; margin: 0;">🔥 VECKANS GASELL (HÖGVOLATIL OUTSIDER)</h2>'
    f'<h4 style="color: #38bdf8; margin-top: 5px;">VALD OUTSIDER: {gazelle["ticker"]} (Volatilitet: {gazelle["volatility"]:.1f}%)</h4>'
    f'<p style="font-size: 1.1rem; margin-bottom: 5px;">'
    f'<b>Slutkurs:</b> {gazelle["close"]:.2f} {gazelle["valuta"]} '
    f'<span style="color: {gazelle_pct_color}; font-weight: bold;">({gazelle["pct"]:+.2f}%)</span> | '
    f'<b>RSI:</b> {gazelle["rsi"]:.1f} | '
    f'<b>20d Högsta:</b> {gazelle["high_20"]:.2f} {gazelle["valuta"]} | '
