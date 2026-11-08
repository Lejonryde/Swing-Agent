import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="AI Swing Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🤖 AI Swing Trading Dashboard")
st.markdown("Här styr du dina två agenter för **Högrisk** (7-10 dagar) och **Lågrisk** (20-30 dagar).")

# Sidebar för inställningar
st.sidebar.header("🔑 API-inställningar")
api_key_input = st.sidebar.text_input("OpenAI API Key (fyll i om Secrets saknas)", type="password")

# Om nyckel finns i secrets eller input
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

# Huvudknappar för att köra agenterna
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Högrisk-agenten")
    st.markdown("Fokus: Småbolag, momentum & breakouts (7-10 dagar).")
    run_high = st.button("Kör Högrisk-analys nu")

with col2:
    st.subheader("🛡️ Lågrisk-agenten")
    st.markdown("Fokus: Large Cap, rekylköp & kapitalbevarande (20-30 dagar).")
    run_low = st.button("Kör Lågrisk-analys nu")


# Funktion för Högrisk
def run_high_risk_agent(api_key):
    if not api_key:
        st.error("Vänligen fyll i din OpenAI API-nyckel i sidofältet eller i Streamlit Secrets!")
        return
    
    tickers = ["VOLV-B.ST", "ERIC-B.ST", "SSAB-B.ST", "SBB-B.ST", "TELIA.ST", "SINCH.ST", "NVDA", "TSLA", "AMD", "PLTR"]
    stock_data_list = []
    
    with st.spinner("Skannar marknaden för Högrisk..."):
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="6mo")
                if df.empty or len(df) < 20:
                    continue
                latest = df.iloc[-1]
                close_price = latest['Close']
                high_20 = df['High'].iloc[-20:].max()
                low_5 = df['Low'].iloc[-5:].min()
                valuta = "SEK" if ticker.endswith(".ST") else "USD"
                
                rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                
                data_summary = f"Ticker: {ticker} | Kurs: {close_price:.2f} {valuta} | 20d Högsta: {high_20:.2f} | 5d Stöd: {low_5:.2f} | RSI: {rsi:.1f}"
                stock_data_list.append(data_summary)
            except:
                continue
                
        market_text = "\n".join(stock_data_list)
        
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Du är en elit-trader som specialiserat sig på kortsiktig swingtrading."},
                {"role": "user", "content": f"Analysera följande data och ge en Top 5-rapport med exakta köplägen, entry, stop-loss och målkurs (+10-15%):\n{market_text}"}
            ]
        )
        st.success("Analys klar!")
        st.markdown(response.choices[0].message.content)


# Funktion för Lågrisk
def run_low_risk_agent(api_key):
    if not api_key:
        st.error("Vänligen fyll i din OpenAI API-nyckel i sidofältet eller i Streamlit Secrets!")
        return
        
    tickers = ["VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "TELIA.ST", "INVE-B.ST", "SHB-A.ST", "AAPL", "MSFT", "GOOGL", "AMZN"]
    stock_data_list = []
    
    with st.spinner("Skannar Large Cap för Lågrisk..."):
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                df = stock.history(period="6mo")
                if df.empty or len(df) < 30:
                    continue
                latest = df.iloc[-1]
                close_price = latest['Close']
                low_10 = df['Low'].iloc[-10:].min()
                valuta = "SEK" if ticker.endswith(".ST") else "USD"
                
                sma_50 = ta.trend.sma_indicator(df['Close
