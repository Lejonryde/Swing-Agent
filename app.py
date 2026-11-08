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

# Mörk terminalstyling
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
    ".stock-box {"
    "    background: #161b22;"
    "    border: 1px solid #30363d;"
    "    border-radius: 8px;"
    "    padding: 12px;"
    "    margin-bottom: 10px;"
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
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Funktion för att få fram företagslogotyp via ikoner/clearbit
def get_company_logo(ticker):
    clean = ticker.split('.')[0].lower()
    # Använder finansiella logotyper eller generiska ikoner
    return f"https://img.logo.dev/ticker:{clean}?token=pk_live_free&size=80"

# Samla marknadsdata för listan direkt
market_data_cache = []
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
        
        market_data_cache.append({
            "ticker": ticker,
            "close": latest_close,
            "pct": pct_change,
            "valuta": valuta,
            "rsi": rsi_val,
            "history": close_ser
        })
    except:
        continue

# Delad skärm
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #38bdf8;'>KÖP & BREAKOUTS</h4>", unsafe_allow_html=True)
    st.write("Aktuell bevakningslista med logotyper och veckografer:")
    
    # Rendera bevakningslistan direkt med logotyper och grafer
    for item in market_data_cache:
        col_logo, col_info = st.columns([1, 4])
        with col_logo:
            # Visar företagsikon
            st.image(f"https://unavatar.io/duckduckgo/{item['ticker'].split('.')[0].lower()}.com", width=45)
        with col_info:
            st.markdown(f"**{item['ticker']}** | {item['close']:.2f} {item['valuta']} "
                        f"<span style='color: {'#22c55e' if item['pct'] >= 0 else '#ef4444'};'>({item['pct']:+.2f}%)</span> | RSI: {item['rsi']:.1f}", 
                        unsafe_allow_html=True)
        st.line_chart(item['history'].tail(7), height=90)
        st.markdown("---")

    run_buy = st.button("🚀 KÖP-ANALYS (AI)", use_container_width=True, key="btn_buy")
    
    if run_buy:
        if not openai_key:
            st.error("❌ Fyll i OpenAI API-nyckel!")
        else:
            with st.spinner("AI analyserar köpcasen..."):
                market_text = "\n".join([f"Ticker: {i['ticker']} | Slutkurs: {i['close']:.2f} {i['valuta']} ({i['pct']:+.2f}%) | RSI: {i['rsi']:.1f}" for i in market_data_cache])
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en elit-trader. Utgå stenhårt från indatan. Leverera en aggressiv rapport på svenska med emojis, exakta entries, tight stop-loss och målkurser."},
                        {"role": "user", "content": f"Vaska fram de 3 starkaste köpcasen:\n{market_text}"}
                    ]
                )
                st.success("AI-RAPPORT KLAR")
                st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171;'>SÄLJ & EXITS</h4>", unsafe_allow_html=True)
    st.write("Aktuell bevakningslista för vinsthemtagning och risker:")
    
    for item in market_data_cache:
        col_logo, col_info = st.columns([1, 4])
        with col_logo:
            st.image(f"https://unavatar.io/duckduckgo/{item['ticker'].split('.')[0].lower()}.com", width=45)
        with col_info:
            st.markdown(f"**{item['ticker']}** | {item['close']:.2f} {item['valuta']} "
                        f"<span style='color: {'#22c55e' if item['pct'] >= 0 else '#ef4444'};'>({item['pct']:+.2f}%)</span> | RSI: {item['rsi']:.1f}", 
                        unsafe_allow_html=True)
        st.line_chart(item['history'].tail(7), height=90)
        st.markdown("---")

    run_sell = st.button("🛑 SÄLJ-ANALYS (AI)", use_container_width=True, key="btn_sell")
    
    if run_sell:
        if not openai_key:
            st.error("❌ Fyll i OpenAI API-nyckel!")
        else:
            with st.spinner("AI analyserar säljsignaler..."):
                market_text = "\n".join([f"Ticker: {i['ticker']} | Slutkurs: {i['close']:.2f} {i['valuta']} ({i['pct']:+.2f}%) | RSI: {i['rsi']:.1f}" for i in market_data_cache])
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en skoningslös riskmanager. Peka ut överköpta aktier och rasrisker på svenska med emojis."},
                        {"role": "user", "content": f"Peka ut de 3 aktier som OMEDELBART SKA SÄLJAS:\n{market_text}"}
                    ]
                )
                st.success("AI-RAPPORT KLAR")
                st.markdown(response.choices[0].message.content)
