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

# Huvudrubrik
st.title("👑 Swing King")

# Sidebar
st.sidebar.header("⚙️ Inställningar")
api_key_input = st.sidebar.text_input("OpenAI API Key (fyll i om Secrets saknas)", type="password")
openai_key = api_key_input if api_key_input else os.environ.get("OPENAI_API_KEY", "")

st.sidebar.subheader("📌 Din Aktiva Bevakningslista")
custom_tickers = st.sidebar.text_area(
    "Ange exakta tickers (separera med komma):", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Delad skärm
col_buy, col_sell = st.columns(2, gap="medium")

# ==================== VÄNSTER HALVA: BLÅ (KÖP) ====================
with col_buy:
    st.markdown("""
        <div style="background-color: rgba(0, 123, 255, 0.12); border: 2px solid #007bff; padding: 20px; border-radius: 12px; margin-bottom: 10px;">
            <h2 style='color: #0056b3; margin: 0;'>🔵 DAGENS FÖRETAG</h2>
            <h3 style='color: #007bff; margin-top: 5px;'>KÖP & BREAKOUTS</h3>
            <p style='color: #333;'>Analyserar din aktiva lista för starka köplägen.</p>
        </div>
    """, unsafe_allow_html=True)
    
    run_buy = st.button("🚀 KÖP-ANALYS", use_container_width=True)
    
    if run_buy:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Hämtar realtidsdata för dina aktier..."):
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
                        
                        stock_data_list.append(f"Ticker: {ticker} | Senaste Kurs: {close:.2f} {valuta} | Högsta (period): {high_20:.2f} | RSI(14): {rsi:.1f}")
                    except:
                        continue
                
                if not stock_data_list:
                    st.warning("Ingen data kunde hämtas för de angivna tickersen. Kontrollera stavningen (t.ex. VOLV-B.ST).")
                else:
                    market_text = "\n".join(stock_data_list)
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är en elit-trader som granskar exakt den data som skickas in. Var stenhård, professionell och ge exakta entry-nivåer och stop-loss."},
                            {"role": "user", "content": f"Baserat enbart på följande indata för mina valda bolag, vaskas fram de bästa köpcasen med exakt entry och målkurs:\n{market_text}"}
                        ]
                    )
                    st.success("Analys klar!")
                    st.markdown(response.choices[0].message.content)


# ==================== HÖGER HALVA: RÖD (SÄLJ) ====================
with col_sell:
    st.markdown("""
        <div style="background-color: rgba(220, 53, 69, 0.12); border: 2px solid #dc3545; padding: 20px; border-radius: 12px; margin-bottom: 10px;">
            <h2 style='color: #a71d2a; margin: 0;'>🔴 DAGENS FÖRETAG</h2>
            <h3 style='color: #dc3545; margin-top: 5px;'>SÄLJ & EXITS</h3>
            <p style='color: #333;'>Analyserar din aktiva lista för vinsthemtagning och stop-loss.</p>
        </div>
    """, unsafe_allow_html=True)
    
    run_sell = st.button("🛑 SÄLJ-ANALYS", use_container_width=True)
    
    if run_sell:
        if not openai_key:
            st.error("Fyll i OpenAI API-nyckel!")
        else:
            stock_data_list = []
            with st.spinner("Hämtar data för exits..."):
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
                        
                        stock_data_list.append(f"Ticker: {ticker} | Senaste Kurs: {close:.2f} {valuta} | Lägsta (period): {low_20:.2f} | RSI(14): {rsi:.1f}")
                    except:
                        continue
                
                if not stock_data_list:
                    st.warning("Ingen data kunde hämtas.")
                else:
                    market_text = "\n".join(stock_data_list)
                    client = OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Du är en riskfokuserad portföljförvaltare. Identifiera överköpta aktier eller risk för ras baserat på datan."},
                            {"role": "user", "content": f"Baserat enbart på följande indata för mina valda bolag, peka ut vilka som bör säljas eller om vinst bör säkras:\n{market_text}"}
                        ]
                    )
                    st.success("Analys klar!")
                    st.markdown(response.choices[0].message.content)
