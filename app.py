import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0 - Paper Trading", page_icon="👑", layout="wide")

CSS_STYLE = """
<style>
html, body, [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #05070b, #0a0e17, #0f172a) !important; color: #e2e8f0 !important; background-attachment: fixed; }
[data-testid="stSidebar"] { background-color: #090d14 !important; border-right: 1px solid #1e293b !important; }
.logo-header-box { background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; box-shadow: 0 0 35px rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 24px; margin-bottom: 25px; text-align: center; }
.logo-title { font-size: 2.8rem; font-weight: 900; letter-spacing: 3px; background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
.logo-sub { color: #94a3b8; font-size: 0.88rem; letter-spacing: 2px; margin-top: 8px; text-transform: uppercase; }
.stock-card { background: rgba(17, 24, 39, 0.92); border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
.argon-badge { background: linear-gradient(90deg, #0284c7, #2563eb); color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; float: right; }
.bear-badge { background: linear-gradient(90deg, #dc2626, #991b1b); color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; float: right; }
.gazelle-badge { background: linear-gradient(90deg, #eab308, #ca8a04); color: #000000; padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; font-weight: 800; float: right; }
.report-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #38bdf8; border-left: 5px solid #38bdf8; border-radius: 8px; padding: 12px 16px; margin: 6px 0 12px 0; font-size: 0.88rem; line-height: 1.55; }
.bear-report-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #ef4444; border-left: 5px solid #ef4444; border-radius: 8px; padding: 12px 16px; margin: 6px 0 12px 0; font-size: 0.88rem; line-height: 1.55; }
.gazelle-box { background: rgba(15, 23, 42, 0.96); border: 2px solid #eab308; box-shadow: 0 0 25px rgba(234, 179, 8, 0.25); border-radius: 14px; padding: 22px; margin: 30px 0 15px 0; line-height: 1.6; }
.sim-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #10b981; border-left: 5px solid #10b981; border-radius: 10px; padding: 18px; margin-bottom: 20px; }
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d %H:%M")

# --- SIDOMENY & PORTFÖJLINSTÄLLNINGAR ---
st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
fiktiv_kassa = st.sidebar.number_input("Fiktiv Startkassa (SEK):", 10000, 1000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)
hold_days = st.sidebar.slider("Mål-innehavstid (dagar):", 3, 20, 7, 1)

DEFAULT_TICKERS = "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=120)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(
    "<div class='logo-header-box'>"
    "<h1 class='logo-title'>👑 SWINGKINGS // ARGON v2.0</h1>"
    f"<div class='logo-sub'>AUTO-REFRESH (1h) // 100K SEK PORTFOLIO // VCP SQUEEZE // {today_str}</div>"
    "</div>",
    unsafe_allow_html=True
)

# TTL satt till 3600 sekunder (1 timme) för automatisk uppdatering av kurser
@st.cache_data(ttl=3600)
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
            close, high, low = df["Close"], df["High"], df["Low"]
            c_now, c_prev = float(close.iloc[-1]), float(close.iloc[-2])
            pct_1d = ((c_now - c_prev) / c_prev) * 100
            c_5d = float(close.iloc[-6]) if len(close) >= 6 else c_prev
            pct_5d = ((c_now - c_5d) / c_5d) * 100

            is_se = ticker.endswith(".ST")
            valuta = "SEK" if is_se else "USD"
            rs_alpha = pct_5d - (omx_5d if is_se else spx_5d)

            rsi_s = ta.momentum.rsi(close=close, window=14)
            rsi_v = float(rsi_s.iloc[-1]) if not pd.isna(rsi_s.iloc[-1]) else 50.0
            sma50 = float(close.tail(50).mean()) if len(close) >= 50 else float(close.tail(20).mean())
            high_20 = float(high.tail(20).max())

            tr = np.maximum(high - low, np.maximum((high - close.shift(1)).abs(), (low - close.shift(1)).abs()))
            atr_14 = float(tr.tail(14).mean())
            dip_high = ((high_20 - c_now) / high_20) * 100
            vol_spread = ((high.tail(20).max() - low.tail(20).min()) / low.tail(20).min()) * 100

            score = 50.0
            if c_now > sma50: score += 12.0
            if rs_alpha > 0.5: score += 10.0
            if 2.0 <= dip_high <= 12.0: score += 14.0
            if 35.0 <= rsi_v <= 56.0: score += 12.0
            argon_score = int(np.clip(score, 10, 99))

            hist_df = pd.DataFrame({
                "Datum": close.tail(20).index.strftime("%m-%d"),
                "Pris": close.tail(20).values
            })

            results.append({
                "ticker": ticker, "close": c_now, "pct": pct_1d, "rs_alpha": rs_alpha,
                "valuta": valuta, "rsi": rsi_v, "atr": atr_14, "volatility": vol_spread,
                "score": argon_score, "history": hist_df
            })
        except Exception:
            continue
    return results

def plot_plotly_chart(hist_df, color_hex, height=110):
    fig = px.line(hist_df, x="Datum", y="Pris", template="plotly_dark")
    fig.update_traces(line=dict(color=color_hex, width=2.5), mode="lines")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        margin=dict(l=0, r=0, t=5, b=0),
        height=height,
        xaxis=dict(showgrid=False, zeroline=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", zeroline=False, color="#94a3b8")
    )
    return fig

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

# --- PAPER TRADING / PORTFÖJ-SIMULATOR ---
top_alloc_stocks = bull_list[:3]
alloc_per_stock = fiktiv_kassa / len(top_alloc_stocks) if top_alloc_stocks else 0

st.markdown(f"""
<div class="sim-box">
    <h3 style="color: #10b981; margin: 0 0 10px 0;">📊 PAPER TRADING & PORTFÖJ-SIMULATOR (100k SEK)</h3>
    <p style="margin: 0; line-height: 1.6;">
        Fördelar din startkassa på <b>{fiktiv_kassa:,.0f} SEK</b> i de 3 högst rankade Bull-aktierna. 
        Kurserna och kassan uppdateras automatiskt varje timme. Innehavstid: <b>{hold_days} dagar</b>.
    </p>
</div>
""", unsafe_allow_html=True)

sim_cols = st.columns(3)
for idx, stock in enumerate(top_alloc_stocks):
    with sim_cols[idx]:
        s_entry = stock["close"] - (0.35 * stock["atr"])
        s_target = s_entry + (3.2 * stock["atr"])
        s_stop = s_entry - (1.6 * stock["atr"])
        shares_sim = int(alloc_per_stock / s_entry) if s_entry > 0 else 0
        est_potential_roi = ((s_target - s_entry) / s_entry) * 100

        st.markdown(f"""
        <div class="stock-card" style="border-color: #10b981;">
            <span class="argon-badge" style="background: #10b981; color: #000;">POSITION #{idx+1}</span>
            <h4 style="margin: 0; color: #34d399;">⚡ {stock['ticker']}</h4>
            <p style="margin: 4px 0; font-size: 0.85rem;">Allokerat: <b>{alloc_per_stock:,.0f} {stock['valuta']}</b> ({shares_sim} st)</p>
            <hr style="border-color: #1e293b; margin: 6px 0;">
            <p style="margin: 2px 0; font-size: 0.8rem;">• Entry: {s_entry:.2f}</p>
            <p style="margin: 2px 0; font-size: 0.8rem;">• Target (+ROI): {s_target:.2f} (<span style="color: #10b981;">+{est_potential_roi:.1f}%</span>)</p>
            <p style="margin: 2px 0; font-size: 0.8rem;">• Stop-Loss: {s_stop:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    for item in bull_list:
        entry_p = item["close"] - (0.35 * item["atr"])
        stop_p = entry_p - max(1.6 * item["atr"], entry_p * 0.035)
        target_p = entry_p + max(3.2 * item["atr"], entry_p * 0.085)
        shares = int((fiktiv_kassa * (risk_pct / 100.0)) / max(entry_p - stop_p, 0.01))
        card_html = (
            "<div class='stock-card'>"
            f"<span class='argon-badge'>SCORE: {item['score']}</span>"
            f"<h3 style='margin: 0; color: #38bdf8;'>⚡ {item['ticker']}</h3>"
            f"<p style='margin: 4px 0;'><b>{item['close']:.2f} {item['valuta']}</b> ({item['pct']:+.2f}%) | RS-Alpha: {item['rs_alpha']:+.1f}%</p>"
            "</div>"
            "<div class='report-box'>"
            f"• <b>Entry:</b> {entry_p:.2f} {item['valuta']} | <b>Target:</b> {target_p:.2f} {item['valuta']} | <b>Stop:</b> {stop_p:.2f} {item['valuta']}<br>"
            f"• <b>Positionsstorlek:</b> <b>{shares} st aktier</b>"
            "</div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.plotly_chart(plot_plotly_chart(item["history"], "#38bdf8", 100), use_container_width=True, config={"displayModeBar": False})

with col_right:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    for item in bear_list:
        s_entry = item["close"] + (0.35 * item["atr"])
        s_stop = s_entry + max(1.5 * item["atr"], s_entry * 0.035)
        s_target = s_entry - max(2.8 * item["atr"], s_entry * 0.08)
        bear_html = (
            "<div class='stock-card'>"
            f"<span class='bear-badge'>SCORE: {item['score']}</span>"
            f"<h3 style='margin: 0; color: #f87171;'>💀 {item['ticker']}</h3>"
            f"<p style='margin: 4px 0;'><b>{item['close']:.2f} {item['valuta']}</b> ({item['pct']:+.2f}%) | RS-Alpha: {item['rs_alpha']:+.1f}%</p>"
            "</div>"
            "<div class='bear-report-box'>"
            f"• <b>Short Entry:</b> {s_entry:.2f} {item['valuta']} | <b>Target:</b> {s_target:.2f} {item['valuta']} | <b>Stop:</b> {s_stop:.2f} {item['valuta']}"
            "</div>"
        )
        st.markdown(bear_html, unsafe_allow_html=True)
        st.plotly_chart(plot_plotly_chart(item["history"], "#f87171", 100), use_container_width=True, config={"displayModeBar": False})

st.markdown("---")
g_entry = gazelle["close"] - (0.35 * gazelle["atr"])
g_stop = g_entry - max(1.6 * gazelle["atr"], g_entry * 0.04)
g_target = g_entry + max(3.5 * gazelle["atr"], g_entry * 0.10)
g_shares = int((fiktiv_kassa * (risk_pct / 100.0)) / max(g_entry - g_stop, 0.01))

gazelle_html = (
    "<div class='gazelle-box'>"
    f"<span class='gazelle-badge'>SCORE: {gazelle['score']} | 20D SPREAD: {gazelle['volatility']:.1f}%</span>"
    f"<h2 style='color: #eab308; margin: 0;'>🔥 VECKANS ARGON-GASELL: {gazelle['ticker']}</h2>"
    f"<p style='margin: 8px 0;'><b>Slutkurs:</b> {gazelle['close']:.2f} {gazelle['valuta']} ({gazelle['pct']:+.2f}%) | <b>RS-Alpha:</b> {gazelle['rs_alpha']:+.1f}% | <b>RSI:</b> {gazelle['rsi']:.1f}</p>"
    "<div style='border-top: 1px solid #334155; padding-top: 10px; margin-top: 8px;'>"
    f"• <b>Entry (Köpzon):</b> {g_entry:.2f} {gazelle['valuta']} | <b>Target (Exit +10% / 3.5x ATR):</b> {g_target:.2f} {gazelle['valuta']} | <b>Stop-Loss:</b> {g_stop:.2f} {gazelle['valuta']}<br>"
    f"• <b>Rekommenderad Positionsstorlek:</b> <b>{g_shares} st aktier</b> (vid {risk_pct}% portföljrisk)"
    "</div>"
    "</div>"
)
st.markdown(gazelle_html, unsafe_allow_html=True)
st.plotly_chart(plot_plotly_chart(gazelle["history"], "#eab308", 150), use_container_width=True, config={"displayModeBar": False})
