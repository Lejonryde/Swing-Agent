import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="Swing King",
    page_icon="👑",
    layout="wide"
)

# Styling för att färglägga Streamlits containrar (Blå vänster, Röd höger)
st.markdown("""
<style>
    /* Blå container (Vänster) */
    [data-testid="stColumn"]:nth-child(1) [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(0, 123, 255, 0.12) !important;
        border: 2px solid #007bff !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    
    /* Röd container (Höger) */
    [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: rgba(220, 53, 69, 0.12) !important;
        border: 2px solid #dc3545 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# Huvudrubrik - Rent och snyggt Swing King
st.title("👑 Swing King")

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

# Delad skärm
col_buy, col_sell = st.columns(2, gap="medium")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    with st.container(border=True):
        st.markdown("<h2 style='color: #0056b3; margin-bottom: 5px;'>🔵 DAGENS FÖRETAG</h2>", unsafe_allow_html=True)
        st.markdown("### KÖP & BREAKOUTS")
        st.write("Skannar marknaden efter de starkaste uppåtgående trenderna.")
        
        run_buy = st.button("🚀 KÖP-ANALYS", use_container_width=True)
        
        if run_buy:
            if not openai_key:
                st.error("Fyll i OpenAI API-nyckel!")
            else:
                stock_data_list = []
                with st.spinner("Analyserar köpkandidater..."):
                    for ticker in tickers_list:
                        try:
                            stock = yf.Ticker(ticker)
                            df = stock.history(period="6mo")
                            if df.empty or len(df) < 20: continue
                            latest = df.iloc[-1]
                            close = latest['Close']
                            high_20 = df['High'].iloc[-20:].max()
                            valuta = "SEK" if ticker.endswith(".ST") else "USD"
                            rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                            
                            stock_data_list.append(f"Ticker: {ticker} | Kurs: {close:.2f} {valuta} | 20d Högsta: {high_20:.2f} | RSI: {rsi:.1f}")
                        except:
                            continue
                    
                    market_text = "\n".join(stock_data_list)
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är en vass swingtrader som levererar skarpa köprekommendationer."},
                            {"role": "user", "content": f"Analysera datan och ge Top 3 aktier för KÖP med exakt entry, stop-loss och målkurs:\n{market_text}"}
                        ]
                    )
                    st.success("Klar!")
                    st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    with st.container(border=True):
        st.markdown("<h2 style='color: #a71d2a; margin-bottom: 5px;'>🔴 DAGENS FÖRETAG</h2>", unsafe_allow_html=True)
        st.markdown("### SÄLJ & EXITS")
        st.write("Identifierar överköpta lägen och vinsthemtagningar.")
        
        run_sell = st.button("🛑 SÄLJ-ANALYS", use_container_width=True)
        
        if run_sell:
            if not openai_key:
                st.error("Fyll i OpenAI API-nyckel!")
            else:
                stock_data_list = []
                with st.spinner("Analyserar säljsignaler..."):
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
                            {"role": "system", "content": "Du är en riskmedveten förvaltare som varnar för risker och rekommenderar vinsthemtagning."},
                            {"role": "user", "content": f"Analysera datan och ge Top 3 aktier som bör SÄLJAS eller där vinst bör säkras:\n{market_text}"}
                        ]
                    )
                    st.success("Klar!")
                    st.markdown(response.choices[0].message.content)
