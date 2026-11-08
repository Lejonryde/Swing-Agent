import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="AI Swing Trading Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Anpassad CSS för att få till snygga blå (köp) och röda (sälj) boxar
st.markdown("""
<style>
    .buy-box {
        background-color: rgba(0, 123, 255, 0.08);
        border: 2px solid #007bff;
        padding: 20px;
        border-radius: 10px;
    }
    .sell-box {
        background-color: rgba(220, 53, 69, 0.08);
        border: 2px solid #dc3545;
        padding: 20px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Rubrik
st.title("⚡ AI Swing Trading Dashboard — Köp & Sälj")
st.caption("Delad terminal för aktiva köplägen och sälj-/exit-signaler.")

# Sidebar
st.sidebar.header("⚙️ Inställningar")
api_key_input = st.sidebar.text_input("OpenAI API Key (fyll i om Secrets saknas)", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("📌 Bevakningslista")
custom_tickers = st.sidebar.text_area(
    "Aktier att analysera (separera med komma):", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST, NVDA, TSLA, AMD, PLTR"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Huvudlayout: Delad skärm (Köp vs Sälj)
col_buy, col_sell = st.columns(2, gap="large")

# ==================== KÖP-SIDAN (BLÅ) ====================
with col_buy:
    st.markdown('<div class="buy-box">', unsafe_allow_html=True)
    st.subheader("🔵 KÖP / BREAKOUTS")
    st.markdown("Fokuserar på att hitta starka köplägen, stöd och uppåtgående momentum.")
    
    run_buy = st.button("🚀 Kör Köp-analys")
    
    if run_buy:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Skannar efter köpkandidater..."):
                for ticker in tickers_list:
                    try:
                        stock = yf.Ticker(ticker)
                        df = stock.history(period="6mo")
                        if df.empty or len(df) < 20: continue
                        latest = df.iloc[-1]
                        close = latest['Close']
                        high_20 = df['High'].iloc[-20:].max()
                        low_5 = df['Low'].iloc[-5:].min()
                        valuta = "SEK" if ticker.endswith(".ST") else "USD"
                        rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                        
                        stock_data_list.append(f"Ticker: {ticker} | Kurs: {close:.2f} {valuta} | 20d Högsta: {high_20:.2f} | 5d Stöd: {low_5:.2f} | RSI: {rsi:.1f}")
                    except:
                        continue
                
                market_text = "\n".join(stock_data_list)
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en aggressiv swingtrader som letar efter de bästa köplägena."},
                        {"role": "user", "content": f"Analysera datan och ge Top 3 aktier för KÖP med exakt entry och stop-loss:\n{market_text}"}
                    ]
                )
                st.success("Köp-analys klar!")
                st.markdown(response.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== SÄLJ-SIDAN (RÖD) ====================
with col_sell:
    st.markdown('<div class="sell-box">', unsafe_allow_html=True)
    st.subheader("🔴 SÄLJ / EXIT & SHORT")
    st.markdown("Fokuserar på överköpta lägen, brutna stöd och vinsthemtagning.")
    
    run_sell = st.button("🛑 Kör Sälj-analys")
    
    if run_sell:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Skannar efter sälj- och exit-signaler..."):
                for ticker in tickers_list:
                    try:
                        stock = yf.Ticker(ticker)
                        df = stock.history(period="6mo")
                        if df.empty or len(df) < 20: continue
                        latest = df.iloc[-1]
                        close = latest['Close']
                        low_20 = df['Low'].iloc[-20:].min()
                        valuta = "SEK" if ticker.endswith(".ST") else "USD"
                        rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                        
                        stock_data_list.append(f"Ticker: {ticker} | Kurs: {close:.2f} {valuta} | 20d Lägsta: {low_20:.2f} | RSI: {rsi:.1f}")
                    except:
                        continue
                
                market_text = "\n".join(stock_data_list)
                client = OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Du är en riskmedveten förvaltare som identifierar överköpta aktier och säljsignaler."},
                        {"role": "user", "content": f"Analysera datan och ge Top 3 aktier som bör SÄLJAS eller där vinst bör säkras (högt RSI, brutna stöd):\n{market_text}"}
                    ]
                )
                st.success("Sälj-analys klar!")
                st.markdown(response.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)
