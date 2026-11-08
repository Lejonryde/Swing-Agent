import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="SWING KING",
    page_icon="👑",
    layout="wide"
)

# Mörk terminal-styling och fyllda kort med glow-effekt
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0b0e14 !important;
        font-family: 'JetBrains Mono', monospace !important;
        color: #e0e6ed !important;
    }
    
    [data-testid="stSidebar"] {
        background-color: #121824 !important;
        border-right: 1px solid #1e293b !important;
    }

    .brand-title {
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #38bdf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Huvudrubrik
st.markdown('<div class="brand-title">👑 SWING KING</div>', unsafe_allow_html=True)
st.caption("ELITE QUANT TERMINAL // BULL & BEAR ENGINE")
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

# Delad skärm
col_buy, col_sell = st.columns(2, gap="large")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    with st.container(border=True):
        st.markdown("""
            <div style="background: linear-gradient(180deg, rgba(0, 123, 255, 0.2) 0%, rgba(15, 23, 42, 0) 100%); padding: 10px; border-radius: 8px;">
                <h2 style='color: #38bdf8; margin: 0; font-weight: 800;'>🔵 DAGENS FÖRETAG</h2>
                <h4 style='color: #94a3b8; margin-top: 5px; text-transform: uppercase;'>KÖP & BREAKOUTS</h4>
                <p style='color: #cbd5e1; font-size: 0.9rem;'>Skannar marknaden efter de starkaste uppåtgående trenderna och volymutbrotten.</p>
            </div>
        """, unsafe_allow_html=True)
        
        run_buy = st.button("🚀 KÖP-ANALYS", use_container_width=True, key="btn_buy")
        
        if run_buy:
            if not openai_key:
                st.error("❌ Fyll i OpenAI API-nyckel!")
            else:
                stock_data_list = []
                with st.spinner("Analyserar köpkandidater..."):
                    for ticker in tickers_list:
                        try:
                            stock = yf.Ticker(ticker)
                            df = stock.history(period="3mo")
                            if df.empty or len(df) < 15: continue
                            latest = df.iloc[-1]
                            close = latest['Close']
                            high_20 = df['High'].max()
                            valuta = "SEK" if ticker.endswith(".ST") else "USD"
                            rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                            
                            stock_data_list.append(f"Ticker: {ticker} | Kurs: {close:.2f} {valuta} | Högsta: {high_20:.2f} | RSI: {rsi:.1f}")
                        except:
                            continue
                    
                    if not stock_data_list:
                        st.warning("Ingen data hittades för angivna tickers.")
                    else:
                        market_text = "\n".join(stock_data_list)
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du är en elit-trader på Lejonryde Capital. Leverera en aggressiv, taggad rapport på Svenska med emojis, exakta entries, tight stop-loss och 10-15% profit-targets."},
                                {"role": "user", "content": f"Baserat på indatan, vaska fram de 3 starkaste köpcasen:\n{market_text}"}
                            ]
                        )
                        st.success("ANALYS KLAR")
                        st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    with st.container(border=True):
        st.markdown("""
            <div style="background: linear-gradient(180deg, rgba(220, 53, 69, 0.2) 0%, rgba(15, 23, 42, 0) 100%); padding: 10px; border-radius: 8px;">
                <h2 style='color: #f87171; margin: 0; font-weight: 800;'>🔴 DAGENS FÖRETAG</h2>
                <h4 style='color: #94a3b8; margin-top: 5px; text-transform: uppercase;'>SÄLJ & EXITS</h4>
                <p style='color: #cbd5e1; font-size: 0.9rem;'>Identifierar överköpta lägen, rasrisker och vinsthemtagningar.</p>
            </div>
        """, unsafe_allow_html=True)
        
        run_sell = st.button("🛑 SÄLJ-ANALYS", use_container_width=True, key="btn_sell")
        
        if run_sell:
            if not openai_key:
                st.error("❌ Fyll i OpenAI API-nyckel!")
            else:
                stock_data_list = []
                with st.spinner("Analyserar säljsignaler..."):
                    for ticker in tickers_list:
                        try:
                            stock = yf.Ticker(ticker)
                            df = stock.history(period="3mo")
                            if df.empty or len(df) < 15: continue
                            latest = df.iloc[-1]
                            close = latest['Close']
                            low_20 = df['Low'].min()
                            valuta = "SEK" if ticker.endswith(".ST") else "USD"
                            rsi = ta.momentum.rsi(df['Close'], window=14).iloc[-1]
                            
                            stock_data_list.append(f"Ticker: {ticker} | Kurs: {close:.2f} {valuta} | Lägsta: {low_20:.2f} | RSI: {rsi:.1f}")
                        except:
                            continue
                    
                    if not stock_data_list:
                        st.warning("Ingen data hittades för angivna tickers.")
                    else:
                        market_text = "\n".join(stock_data_list)
                        client = OpenAI(api_key=openai_key)
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[
                                {"role": "system", "content": "Du är en skoningslös riskmanager på Lejonryde Capital. Identifiera överköpta aktier och rasrisk. Använd ett stenhårt, varningstungt språk med emojis."},
                                {"role": "user", "content": f"Baserat på indatan, peka ut de 3 aktier som OMEDELBART SKA SÄLJAS:\n{market_text}"}
                            ]
                        )
                        st.success("ANALYS KLAR")
                        st.markdown(response.choices[0].message.content)
