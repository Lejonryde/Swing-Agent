import os
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from openai import OpenAI

# Sidkonfiguration
st.set_page_config(
    page_title="SWINGKINGS",
    page_icon="👑",
    layout="wide"
)

# Mörk neonglödande styling
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
        margin-bottom: 12px;
        backdrop-filter: blur(5px);
    }
    .report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #38bdf8;
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 18px;
        font-size: 0.9rem;
    }
    .bear-report-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 18px;
        font-size: 0.9rem;
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
        margin-top: 35px;
        margin-bottom: 30px;
        backdrop-filter: blur(5px);
    }
</style>
""", unsafe_allow_html=True)

# Dagens datum
today_str = datetime.now().strftime("%Y-%m-%d")

# Säkert hämtande av OpenAI API-nyckel från Streamlit Secrets
openai_key = ""
try:
    if "OPENAI_API_KEY" in st.secrets:
        openai_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    pass

if not openai_key:
    openai_key = os.environ.get("OPENAI_API_KEY", "")

# Sidebar - Bevakningslista
st.sidebar.header("🕹️ CONTROL PANEL")
st.sidebar.subheader("🎯 BEVAKNINGSLISTA")
custom_tickers = st.sidebar.text_area(
    "Aktiva tickers:", 
    "VOLV-B.ST, ERIC-B.ST, SSAB-B.ST, SBB-B.ST, TELIA.ST, SINCH.ST, "
    "EVOL.ST, BOL.ST, NDA-SE.ST, GETIB.ST, HEXA-B.ST, ATCO-A.ST, "
    "SAND.ST, ABB.ST, INVE-B.ST, HM-B.ST, SEB-A.ST, SHB-A.ST, "
    "NVDA, TSLA, AMD, PLTR, AAPL, MSFT"
)
tickers_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]

# Inramad SWINGKINGS Logotyp
st.markdown(
    f'<div class="logo-header-box">'
    f'<h1 class="logo-title">👑 SWINGKINGS</h1>'
    f'<div class="logo-sub">SWINGTRADE ENGINE (10+10 AKTIER // 7-10 DAGAR) // DATUM: {today_str}</div>'
    f'</div>',
    unsafe_allow_html=True
)

# Hämtar marknadsdata säkert
market_data = []
for ticker in tickers_list:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if df.empty or len(df) < 3:
            continue
        close_ser = df['Close']
        latest_close = close_ser.iloc[-1]
        prev_close = close_ser.iloc[-2]
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        valuta = "SEK" if ticker.endswith(".ST") else "USD"
        rsi_val = ta.momentum.rsi(close=close_ser, window=min(14, len(close_ser)-1)).iloc[-1]
        high_20 = df['High'].max()
        low_20 = df['Low'].min()
        
        # Beräkna avstånd till 20d högsta för att mäta dipp-potential i uppåtgående trend
        dip_from_peak = ((high_20 - latest_close) / high_20) * 100
        volatility_spread = ((high_20 - low_20) / low_20) * 100
        
        market_data.append({
            "ticker": ticker,
            "close": latest_close,
            "pct": pct_change,
            "valuta": valuta,
            "rsi": rsi_val,
            "high_20": high_20,
            "low_20": low_20,
            "dip_from_peak": dip_from_peak,
            "volatility": volatility_spread,
            "history": close_ser.tail(10)
        })
    except Exception:
        continue

if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas. Kontrollera dina tickers i sidopanelen.")
    st.stop()

# Funktion för fördjupad analys inklusive dipp-potential i starka trendbolag
def get_advanced_analysis(ticker, side, rsi, pct, dip_peak):
    t = ticker.upper()
    if "VOLV" in t:
        return f"Cyklisk verkstadsjätte med starka kassaflöden i en strukturellt uppåtgående industri. <b>Dipp-potential:</b> Aktien befinner sig i en tillfällig rekyl ({dip_from_peak:.1f}% från 20d topp) vilket skapar en klassisk 'buy-the-dip'-möjlighet i en intakt primärtrend."
    elif "ERIC" in t:
        return f"Global telekomledare som gynnas av strukturella 5G- och nätverksuppgraderingar. <b>Dipp-potential:</b> Tillfälligt säljtryck har tryckt ner RSI till {rsi:.1f}, vilket ger en tydlig mean-reversion-potential mot glidande medelvärden."
    elif "SSAB" in t:
        return f"Stål- och råvarusektorn uppvisar hög känslighet för globala konjunktursvängningar. <b>Dipp-potential:</b> Den kortsiktiga svackan utgör en attraktiv risk/reward för en snabb rekylstuds upp mot tidigare motstånd."
    elif "SBB" in t:
        return f"Fastighetsbolag under hård press från räntekänslighet och svaga kapitalflöden. <b>Trendfaktor:</b> Saknar förnyat köparintresse; tillfälliga uppstudsar används av institutioner för exit."
    elif "TELIA" in t:
        return f"Defensivt kassaflödesbolag. <b>Trendfaktor:</b> Låg volatilitet och begränsad tillväxtpotential gör att aktien tenderar att handlas sidledes utan det momentum som krävs för kortsiktiga swingvinster."
    elif "NVDA" in t or "AMD" in t or "TSLA" in t or "PLTR" in t or "AAPL" in t or "MSFT" in t:
        if side == "bull":
            return f"Marknadsledande inom tillväxt- och AI-sektorn med extremt starka institutionella flöden. <b>Dipp-potential:</b> Hälsosam intradagsdipp ({dip_from_peak:.1f}% från topp) i en urstark uppåtgående bransch ger idealisk hävstång för en 7-dagars studs."
        else:
            return f"Högbeta tech-bolag som uppvisar kortsiktig överhettning. <b>Trendfaktor:</b> Vinsthemtagningar och fallande momentum vid motståndsnivåer ökar risken för ytterligare nedsida."
    elif "EVOL" in t:
        return f"Marknadsledare inom live-casino med branschledande marginaler. <b>Dipp-potential:</b> Tillfällig makrooro skapar en omotiverad svacka i ett tillväxtstarkt bolag, vilket bäddar för en kraftfull återhämtning."
    elif "BOL" in t or "SAND" in t:
        return f"Industri- och gruvbolag bundet till den globala cykeln. <b>Dipp-potential:</b> Rekylen ned mot tekniska stödnivåer ger en gynnsam ingångspunkt för swingtraders som vill fiska upp billiga cykliska tillgångar."
    else:
        if side == "bull":
            return f"Bolaget uppvisar fundamental styrka trots tillfälligt externt säljtryck. <b>Dipp-potential:</b> Den tillfälliga svackan har rensat ut kortsiktiga spekulanter och öppnat upp ett fördelaktigt uppsidefönster."
        else:
