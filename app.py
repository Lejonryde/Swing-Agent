import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="AI Swing Trading Terminal",
    page_icon="⚡",
    layout="wide"
)

# Anpassad CSS för drama, färgboxar och stil
st.markdown("""
<style>
    .buy-box {
        background: linear-gradient(135deg, rgba(0, 123, 255, 0.12) 0%, rgba(0, 200, 255, 0.03) 100%);
        border: 2px solid #007bff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.1);
    }
    .sell-box {
        background: linear-gradient(135deg, rgba(220, 53, 69, 0.12) 0%, rgba(255, 50, 50, 0.03) 100%);
        border: 2px solid #dc3545;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.1);
    }
    .main-header {
        display: flex;
        align-items: center;
        gap: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Topp-banner med logotype-känsla och drama
st.markdown("""
    <div class="main-header">
        <h1>⚡ LEJONRYDE CAPITAL // SWING TERMINAL</h1>
    </div>
""", unsafe_allow_html=True)
st.caption("🚨 AI-driven krigszon för kortsiktig momentum-trading, utbrott och skoningslösa exits.")

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

# ==================== KÖP-SIDAN (BLÅ - BULLISH DRAMA) ====================
with col_buy:
    st.markdown('<div class="buy-box">', unsafe_allow_html=True)
    st.subheader("🚀 BULL-PENNA // KÖPLÄGEN & BREAKOUTS")
    st.markdown("*Här jagar vi de blodiga rörelserna uppåt. Hög energi, perfekta entrisar.*")
    
    run_buy = st.button("🔥 UTELÖS KÖP-ATTACK (START)", use_container_width=True)
    
    if run_buy:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Letar efter explosioner i orderdjupet..."):
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
                        {"role": "system", "content": "Du är en kompromisslös, aggressiv kryptisk swingtrader (Jordan Belfort-vibe) som älskar risk och stora uppgångar. Använd dramatiskt, eldigt språk med emojis."},
                        {"role": "user", "content": f"Analysera datan med maximalt driv och ge Top 3 aktier för KÖP. Sätt eld på rapporten med exakta entry-nivåer, tight stop-loss och saftig målkurs:\n{market_text}"}
                    ]
                )
                st.success(" attacken är redo!")
                st.markdown(response.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)


# ==================== SÄLJ-SIDAN (RÖD - BEARISH DRAMA) ====================
with col_sell:
    st.markdown('<div class="sell-box">', unsafe_allow_html=True)
    st.subheader("💀 BEAR-TRAP // EXIT & VINSTHEMTAGNING")
    st.markdown("*Här klipper vi förlorarna skoningslöst och säkrar vinsten innan marknaden gör det åt oss.*")
    
    run_sell = st.button("🛑 UTELÖS SLakt-ATTACK (START)", use_container_width=True)
    
    if run_sell:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Letar efter blodbad, överköpta monster och brutna stöd..."):
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
                        {"role": "system", "content": "Du är en benhård riskhanterare som hatar att förlora pengar. Varnar dramatiskt för överköpta aktier, stup och röd panik. Använd stenhårt språk med emojis."},
                        {"role": "user", "content": f"Analysera datan och ge Top 3 aktier som OMEDELBART SKA SÄLJAS eller blankas (högt RSI, rasrisk, brutna stöd). Var skoningslös:\n{market_text}"}
                    ]
                )
                st.success("Slakt-rapport klar!")
                st.markdown(response.choices[0].message.content)
    st.markdown('</div>', unsafe_allow_html=True)
