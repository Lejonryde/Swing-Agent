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

# ULTRA-MODERN DARK TERMINAL CSS
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

    .bull-box {
        background: linear-gradient(180deg, rgba(0, 123, 255, 0.18) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 2px solid #0284c7;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.25);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .bear-box {
        background: linear-gradient(180deg, rgba(220, 53, 69, 0.18) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 2px solid #dc2626;
        box-shadow: 0 0 15px rgba(220, 38, 38, 0.25);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Huvudrubrik
st.markdown('<div class="brand-title">👑 SWING KING</div>', unsafe_allow_html=True)
st.caption("LEJONRYDE CAPITAL QUANT ENGINE // FREDAGSRAPPORT & BREAKOUT PROTOCOL")
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
    st.markdown("""
        <div class="bull-box">
            <h2 style='color: #38bdf8; margin: 0; font-weight: 800;'>🔵 DAGENS FÖRETAG</h2>
            <h4 style='color: #94a3b8; margin-top: 5px; text-transform: uppercase;'>KÖP & BREAKOUTS (FREDAGSSLUT)</h4>
            <p style='color: #cbd5e1; font-size: 0.9rem;'>Analyserar fredagens stängningskurser och volymutbrott för din bevakningslista.</p>
        </div>
    """, unsafe_allow_html=True)
    
    run_buy = st.button("🚀 KÖP-ANALYS", use_container_width=True, key="btn_buy")
    
    if run_buy:
        if not openai_key:
            st.error("❌ Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Hämtar fredagsdata för dina aktier..."):
                for ticker in tickers_list:
                    try:
                        stock = yf.Ticker(ticker)
                        df = stock.history(period="1mo")
                        if df.empty or len(df) < 5:
                            continue
                        
                        close_ser = df['Close']
                        friday_close = close_ser.iloc[-1]
                        prev_close = close_ser.iloc[-2]
                        pct_change = ((friday_close - prev_close) / prev_close) * 100
                        high_20 = df['High'].max()
                        valuta = "SEK" if ticker.endswith(".ST") else "USD"
                        
                        rsi_series = ta.momentum.rsi(close=close_ser, window=14)
                        rsi_val = rsi_series.iloc[-1]
                        
                        info_str = f"Ticker: {ticker} | Fredag Slutkurs: {friday_close:.2f} {valuta} ({pct_change:+.2f}%) | 20d Högsta: {high_20:.2f} | RSI: {rsi_val:.1f}"
                        stock_data_list.append(info_str)
                    except Exception:
                        continue

                if not stock_data_list:
                    st.warning("Ingen data hittades för angivna tickers.")
                else:
                    market_text = "\n".join(stock_data_list)
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är en elit-trader på Lejonryde Capital. Utgå stenhårt från fredagens slutkurser och indata. Leverera en aggressiv rapport på svenska med emojis, exakta entries, tight stop-loss och målkurser."},
                            {"role": "user", "content": f"Baserat på fredagsdata, vaska fram de 3 starkaste köpcasen:\n{market_text}"}
                        ]
                    )
                    st.success("ANALYS KLAR")
                    st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    st.markdown("""
        <div class="bear-box">
            <h2 style='color: #f87171; margin: 0; font-weight: 800;'>🔴 DAGENS FÖRETAG</h2>
            <h4 style='color:
