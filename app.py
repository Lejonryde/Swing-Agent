import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0", page_icon="👑", layout="wide")

CSS_STYLE = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #05070b, #0a0e17, #0f172a) !important;
    color: #e2e8f0 !important;
    background-attachment: fixed;
}
[data-testid="stSidebar"] {
    background-color: #090d14 !important;
    border-right: 1px solid #1e293b !important;
}
.logo-header-box {
    background: rgba(15, 23, 42, 0.95);
    border: 2px solid #38bdf8;
    box-shadow: 0 0 35px rgba(56, 189, 248, 0.25);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 25px;
    text-align: center;
}
.logo-title {
    font-size: 2.8rem;
    font-weight: 900;
    letter-spacing: 3px;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.logo-sub {
    color: #94a3b8;
    font-size: 0.88rem;
    letter-spacing: 2px;
    margin-top: 8px;
    text-transform: uppercase;
}
.stock-card {
    background: rgba(17, 24, 39, 0.92);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 10px;
}
.argon-badge {
    background: linear-gradient(90deg, #0284c7, #2563eb);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    float: right;
}
.bear-badge {
    background: linear-gradient(90deg, #dc2626, #991b1b);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 700;
    float: right;
}
.report-box {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid #38bdf8;
    border-left: 5px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 22px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.bear-report-box {
    background: rgba(15, 23, 42, 0.94);
    border: 1px solid #ef4444;
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 22px;
    font-size: 0.88rem;
    line-height: 1.55;
}
.gazelle-box {
    background: rgba(15, 23, 42, 0.96);
    border: 2px solid #eab308;
    box-shadow: 0 0 25px rgba(234, 179, 8, 0.25);
    border-radius: 14px;
    padding: 22px;
    margin-top: 30px;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d")

st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
portfolio_sek = st.sidebar.number_input("Portföljstorlek:", 10000, 10000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)
max_risk_cash = portfolio_sek * (risk_pct / 100.0)

DEFAULT_TICKERS = "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=120)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(f"""
<div class="logo-header-box">
    <h1 class="logo-title">👑 SWINGKINGS // ARGON v2.0</h1>
    <div class="logo-sub">ATR-DYNAMIC LEVELS // VCP SQUEEZE // RS-ALPHA SCANNER // {today_str}</div>
</div>
""", unsafe_allow_html=True)

@st.cache_data(ttl=900)
def fetch_argon_v2_data(tickers):
    omx_5d, spx_5d = 0.0, 0.0
    try:
        omx = yf.Ticker("^OMX").history(period="1mo")
        if len(omx) >= 6:
            omx_5d = ((float(omx["Close"].iloc[-1]) - float(omx["Close"].iloc[-6])) / float(omx["Close"].iloc[-6])) * 100
    except Exception:
        pass
    try:
        spx = yf.Ticker("^GSPC").history(period="1mo")
        if len(spx) >= 6:
            spx_5d = ((float(spx["Close"].iloc[-1]) - float(spx["Close"].iloc[-6])) / float(spx["Close"].iloc[-6])) * 100
    except Exception:
        pass

    results = []
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            if df.empty or len(df) < 20:
                continue
            close, high, low, vol = df["Close"], df["High"], df["Low"], df["Volume"]
            c_now, c_prev, y_high = float(close.iloc[-1]), float(close.iloc[-2]), float(high.iloc[-2])
            pct_1d = ((c_now - c_prev) / c_prev) * 100
            c_5d = float(close.iloc[-6]) if len(close) >= 6 else c_prev
            pct_5d = ((c_now - c_5d) / c_5d) * 100

            is_se = ticker.endswith(".ST")
            valuta = "SEK" if is_se else "USD"
            rs_alpha = pct_5d - (omx_5d if is_se else spx_5d)

            rsi_s = ta.momentum.rsi(close=close, window=14)
            rsi_v = float(rsi_s.iloc[-1]) if not pd.isna(rsi_s.iloc[-1]) else 50.0
            ema10 = float(close.ewm(span=10, adjust=False).mean().iloc[-1])
            sma20 = float(close.tail(20).mean())
            sma50 = float(close.tail(50).mean()) if len(close) >= 50 else sma20
            high_20 = float(high.tail(20).max())

            tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
            atr_14 = float(tr.tail(14).mean())
            atr_pct = (atr_14 / c_now) * 100

            avg_vol = float(vol.tail(20).mean())
            rvol = (float(vol.iloc[-1]) / avg_vol) if avg_vol > 0 else 1.0
            dip_high = ((high_20 - c_now) / high_20) * 100
            vol_spread = ((high.tail(20).max() - low.tail(20).min()) / low.tail(20).min()) * 100

            score = 50.0
            if c_now > sma50: score += 12.0
            if sma20 >= sma50: score += 8.0
            if rs_alpha > 0.5: score += 10.0
            if 2.0 <= dip_high <= 12.0 and c_now >= sma50 * 0.95: score += 14.0
            elif dip_high < 2.0 and pct_1d > 0: score += 8.0
            if 35.0 <= rsi_v <= 56.0: score += 12.0
            elif rsi_v < 30.0: score -= 10.0
            argon_score = int(np.clip(score, 10, 99))

            results.append({
                "ticker": ticker, "close": c_now, "y_high": y_high, "pct": pct_1d,
                "rs_alpha": rs_alpha, "valuta": valuta, "rsi": rsi_v, "ema10": ema10,
                "sma50": sma50, "high_20": high_20, "dip": dip_high, "atr": atr_14,
                "atr_pct": atr_pct, "rvol": rvol, "volatility": vol_spread,
                "score": argon_score, "tag": "⚡ MOMENTUM & ATR SETUP", "history": close.tail(15)
            })
        except Exception:
            continue
    return results

market_data = fetch_argon_v2_data(tickers_list)
if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas.")
    st.stop()

sorted_argon = sorted(market_data, key=lambda x: (x["score"], x["rs_alpha"]), reverse=True)
bull_list = sorted_argon[:10]
bull_set = {i["ticker"] for i in bull_list}
bear_list = sorted([d for d in market_data if d["ticker"] not in bull_set], key=lambda x: (x["score"], x["rs_alpha"]))[:10]
bear_set = {i["ticker"] for i in bear_list}
gazelle = max([d for d in market_data if d["ticker"] not in bull_set and d["ticker"] not in bear_set] or market_data, key=lambda x: x["volatility"])

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    for item in bull_list:
        entry_p = item["close"] - (0.35 * item["atr"])
        stop_p = entry_p - max(1.6 * item["atr"], entry_p * 0.035)
        target_p = entry_p + max(3.2 * item["atr"], entry_p * 0.085)
        shares = int((portfolio_sek * (risk_pct / 100.0)) / max(entry_p - stop_p, 0.01))

        st.markdown(f"""
        <div class="stock-card">
            <span class="argon-badge">SCORE: {item['score']}</span>
            <h3 style="margin: 0; color: #38bdf8;">⚡ {item['ticker']}
