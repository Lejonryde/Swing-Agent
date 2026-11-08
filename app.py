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

# Mörk terminalstyling med stöd för logotyper och boxar
st.markdown(
    "<style>"
    "html, body, [data-testid='stAppViewContainer'] {"
    "    background-color: #0b0e14 !important;"
    "    color: #e0e6ed !important;"
    "}"
    "[data-testid='stSidebar'] {"
    "    background-color: #121824 !important;"
    "}"
    ".brand-title {"
    "    font-size: 2.2rem;"
    "    font-weight: 800;"
    "    color: #38bdf8;"
    "}"
    ".stock-card {"
    "    background: #161b22;"
    "    border: 1px solid #30363d;"
    "    border-radius: 8px;"
    "    padding: 12px;"
    "    margin-bottom: 12px;"
    "    display: flex;"
    "    align-items: center;"
    "    gap: 15px;"
    "}"
    "</style>",
    unsafe_allow_html=True
)

# Huvudrubrik
st.markdown('<div class="brand-title">👑 SWING KING TERMINAL</div>', unsafe_allow_html=True)
st.caption("QUANT ENGINE // BREAKOUT & EXIT PROTOCOL")
st.markdown("---")

# Sidebar
st.sidebar.header("🕹️ CONTROL PANEL")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST, NVDA, TSLA, AMD, PLTR"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Hämtar marknadsdata för alla aktier
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
        
        # Hämta logotyp via Clearbit / unavatar baserat på domän
        clean_name = ticker.split('.')[0].lower()
        logo_url = f"https://logo.clearbit.com/{clean_name}.com"
        
        market_data.append({
            "ticker": ticker,
            "close": latest_close,
            "pct": pct_change,
            "valuta": valuta,
            "rsi": rsi_val,
            "history": close_ser,
            "logo": logo_url
        })
    except:
        continue

# Dela upp i Bull (positivt momentum / starkare RSI / uppgång) och Bear (svaghet / låg RSI / nedgång)
bull_candidates = sorted([d for d in market_data if d['pct'] >= 0 or d['rsi'] > 50], key=lambda x: x['pct'], reverse=True)
bear_candidates = sorted([d for d in market_data if d['pct'] < 0 or d['rsi'] < 45], key=lambda x: x['pct'])

# Fallback om listorna blir tomma
if not bull_candidates: bull_candidates = market_data[:3]
if not bear_candidates: bear_candidates = market_data[-3:]

# Delad skärm
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (KÖP / BULL) ====================
with col_buy:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #38bdf8;'>KÖP & BREAKOUTS</h4>", unsafe_allow_html=True)
    st.write("Skannade köpkandidater med starkt momentum:")
    
    for item in bull_candidates[:4]:
        # HTML-kort med företagslogotyp och data
        st.markdown(f"""
            <div class="stock-card">
                <img src="{item['logo']}" width="40" height="40" style="border-radius: 6px; background: #fff; padding: 2px;" onerror="this.style.display='none'">
                <div>
                    <h3 style="margin: 0; color: #38bdf8;">{item['ticker']}</h3>
                    <p style="margin: 2px 0; font-size: 0.95rem;"><b>{item['close']:.2f} {item['valuta']}</b> <span style="color: #22c55e;">({item['pct']:+.2f}%)</span> | RSI: {item['rsi']:.1f}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.line_chart(item['history'].tail(7), height=80)

    run_buy = st.button("🚀 KÖP-ANALYS (AI)", use_container_width=True, key="btn_buy")
    
    if run_buy:
        if not openai_key:
            st.error("❌ Fyll i OpenAI API-nyckel!")
        else:
            with st.spinner("AI vaskar fram bästa köpcasen..."):
                market_text = "\n".join([f"Ticker: {i['ticker']} | Kurs: {i['close']:.2f} {i['valuta']} ({i['pct']:+.2f}%) | RSI: {i['rsi']:.1f}" for i in bull_candidates])
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en elit-trader. Utgå stenhårt från indatan. Leverera en aggressiv rapport på svenska med emojis, exakta entries, tight stop-loss och målkurser."},
                        {"role": "user", "content": f"Vaska fram de 3 starkaste köpcasen bland dessa:\n{market_text}"}
                    ]
                )
                st.success("AI-RAPPORT KLAR")
                st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ / BEAR) ====================
with col_sell:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171;'>SÄLJ & EXITS</h4>", unsafe_allow_html=True)
    st.write("Skannade säljkandidater med svaghet eller risk:")
    
    for item in bear_candidates[:4]:
        st.markdown(f"""
            <div class="stock-card">
                <img src="{item['logo']}" width="40" height="40" style="border-radius: 6px; background: #fff; padding: 2px;" onerror="this.style.display='none'">
                <div>
                    <h3 style="margin: 0; color: #f87171;">{item['ticker']}</h3>
                    <p style="margin: 2px 0; font-size: 0.95rem;"><b>{item['close']:.2f} {item['valuta']}</b> <span style="color: #ef4444;">({item['pct']:+.2f}%)</span> | RSI: {item['rsi']:.1f}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.line_chart(item['history'].tail(7), height=80)

    run_sell = st.button("🛑 SÄLJ-ANALYS (AI)", use_container_width=True, key="btn_sell")
    
    if run_sell:
        if not openai_key:
            st.error("❌ Fyll i OpenAI API-nyckel!")
        else:
            with st.spinner("AI analyserar säljsignaler..."):
                market_text = "\n".join([f"Ticker: {i['ticker']} | Kurs: {i['close']:.2f} {i['valuta']} ({i['pct']:+.2f}%) | RSI: {i['rsi']:.1f}" for i in bear_candidates])
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en skoningslös riskmanager. Peka ut överköpta aktier och rasrisker på svenska med emojis."},
                        {"role": "user", "content": f"Peka ut de 3 aktier som OMEDELBART SKA SÄLJAS bland dessa:\n{market_text}"}
                    ]
                )
                st.success("AI-RAPPORT KLAR")
                st.markdown(response.choices[0].message.content)
