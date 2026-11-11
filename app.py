import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import altair as alt
from datetime import datetime, timedelta

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0", page_icon="👑", layout="wide")

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

today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d %H:%M")

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
    "<div class='logo-sub'>PAPER TRADING ENGINE // 100K SEK // AUTO-REFRESH (1H) // " + today_str + "</div>"
    "</div>",
    unsafe_allow_html=True
)

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

def plot_neon_chart(hist_df, color_hex, height=120):
    chart = alt.Chart(hist_df).mark_area(
        line={"color": color_hex, "strokeWidth": 2.5},
        color=color_hex,
        fillOpacity=0.18
    ).encode(
        x=alt.X("Datum:N", title=None, axis=alt.Axis(labelColor="#94a3b8", grid=False, labelAngle=0)),
        y=alt.Y("Pris:Q", title=None, scale=alt.Scale(zero=False), axis=alt.Axis(labelColor="#94a3b8", gridColor="#1e293b")),
        tooltip=["Datum", alt.Tooltip("Pris:Q", format=".2f")]
    ).properties(height=height).configure_view(strokeWidth=0)
    return chart

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

st.markdown(
    "<div class='sim-box'>"
    "<h3 style='color: #10b981; margin: 0 0 10px 0;'>📊 PAPER TRADING & PORTFÖJ-SIMULATOR</h3>"
    "<p style='margin: 0; line-height: 1.6;'>"
    "Fördelar din startkassa på <b>" + f"{fiktiv_kassa:,.0f}" + " SEK</b> i de 3 högst rankade Bull-aktierna. "
    "Innehavstid: <b>" + str(hold_days) + " dagar</b> med automatisk timuppdatering."
    "</p>"
    "</div>",
    unsafe_allow_html=True
)

sim_cols = st.columns(3)
for idx, stock in enumerate(top_alloc_stocks):
    with sim_cols[idx]:
        s_entry = stock["close"] - (0.35 * stock["atr"])
        s_target = s_entry + (3.2 * stock["atr"])
        s_stop = s_entry - (1.6 * stock["atr"])
        shares_sim = int(alloc_per_stock / s_entry) if s_entry > 0 else 0
        
        entry_date_str = today_dt.strftime("%Y-%m-%d")
        exit_date_dt = today_dt + timedelta(days=hold_days)
        exit_date_str = exit_date_dt.strftime("%Y-%m-%d")
        
        pct_since_entry = ((stock["close"] - s_entry) / s_entry) * 100
        roi_color = "#10b981" if pct_since_entry >= 0 else "#ef4444"

        card_text = (
            "<div class='stock-card' style='border-color: #10b981;'>"
            "<span class='argon-badge' style='background: #10b981; color: #000;'>POSITION #" + str(idx+1) + "</span>"
            "<h4 style='margin: 0; color: #34d399;'>⚡ " + stock['ticker'] + "</h4>"
            "<p style='margin: 4px 0; font-size: 0.85rem;'>Allokerat: <b>" + f"{alloc_per_stock:,.0f}" + " " + stock['valuta'] + "</b> (" + str(shares_sim) + " st)</p>"
            "<hr style='border-color: #1e293b; margin: 6px 0;'>"
            "<p style='margin: 2px 0; font-size: 0.8rem;'>• <b>Entry-datum:</b> " + entry_date_str + "</p>"
            "<p style='margin: 2px 0; font-size: 0.8rem;'>• <b>Planerad Exit:</b> " + exit_date_str + "</p>"
            "<p style='margin: 2px 0; font-size: 0.8rem;'>• <b>Entrykurs:</b> " + f"{s_entry:.2f}" + " " + stock['valuta'] + "</p>"
            "<p style='margin: 2px 0; font-size: 0.8rem;'>• <b>Utveckling:</b> <span style='color: " + roi_color + "; font-weight: bold;'>" + f"{pct_since_entry:+.2f}%</span></p>"
            "<p style='margin: 2px 0; font-size: 0.8rem;'>• <b>Target:</b> " + f"{s_target:.2f}" + " | <b>Stop:</b> " + f"{s_stop:.2f}" + "</p>"
            "</div>"
        )
        st.markdown(card_text, unsafe_allow_html=True)

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
            "<span class='argon-badge'>SCORE: " + str(item['score']) + "</span>"
            "<h3 style='margin: 0; color: #38bdf8;'>⚡ " + item['ticker'] + "</h3>"
            "<p style='margin: 4px 0;'><b>" + f"{item['close']:.2f}" + " " + item['valuta'] + "</b> (" + f"{item['pct']:+.2f}" + "%) | RS-Alpha: " + f"{item['rs_alpha']:+.1f}%</p>"
            "</div>"
            "<div class='report-box'>"
            "• <b>Entry:</b> " + f"{entry_p:.2f}" + " " + item['valuta'] + " | <b>Target:</b> " + f"{target_p:.2f}" + " | <b>Stop:</b> " + f"{stop_p:.2f}" + "<br>"
            "• <b>Positionsstorlek:</b> <b>" + str(shares) + " st aktier</b>"
            "</div>"
        )
        st.markdown(card_html, unsafe_allow_html=True)
        st.altair_chart(plot_neon_chart(item["history"], "#38bdf8", 115), use_container_width=True)

with col_right:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    for item in bear_list:
        s_entry = item["close"] + (0.35 * item["atr"])
        s_stop = s_entry + max(1.5 * item["atr"], s_entry * 0.035)
        s_target = s_entry - max(2.8 * item["atr"], s_entry * 0.08)
        bear_html = (
            "<div class='stock-card'>"
            "<span class='bear-badge'>SCORE: " + str(item['score']) + "</span>"
            "<h3 style='margin: 0; color: #f87171;'>💀 " + item['ticker'] + "</h3>"
            "<p style='margin: 4px 0;'><b>" + f"{item['close']:.2f}" + " " + item['valuta'] + "</b> (" + f"{item['pct']:+.2f}" + "%) | RS-Alpha: " + f"{item['rs_alpha']:+.1f}%</p>"
            "</div>"
            "<div class='bear-report-box'>"
            "• <b>Short Entry:</b> " + f"{s_entry:.2f}" + " " + item['valuta'] + " | <b>Target:</b> " + f"{s_target:.2f}" + " | <b>Stop:</b> " + f"{s_stop:.2f}"
            "</div>"
        )
        st.markdown(bear_html, unsafe_allow_html=True)
        st.altair_chart(plot_neon_chart(item["history"], "#f87171", 115), use_container_width=True)

st.markdown("---")
g_entry = gazelle["close"] - (0.35 * gazelle["atr"])
g_stop = g_entry - max(1.6 * gazelle["atr"], g_entry * 0.04)
g_target = g_entry + max(3.5 * gazelle["atr"], g_entry * 0.10)
g_shares = int((fiktiv_kassa * (risk_pct / 100.0)) / max(g_entry - g_stop, 0.01))

gazelle_html = (
    "<div class='gazelle-box'>"
    "<span class='gazelle-badge'>SCORE: " + str(gazelle['score']) + " | 20D SPREAD: " + f"{gazelle['volatility']:.1f}" + "%</span>"
    "<h2 style='color: #eab308; margin: 0;'>🔥 VECKANS ARGON-GASELL: " + gazelle['ticker'] + "</h2>"
    "<p style='margin: 8px 0;'><b>Slutkurs:</b> " + f"{gazelle['close']:.2f}" + " " + gazelle['valuta'] + " (" + f"{gazelle['pct']:+.2f}" + "%) | <b>RS-Alpha:</b> " + f"{gazelle['rs_alpha']:+.1f}" + "% | <b>RSI:</b> " + f"{gazelle['rsi']:.1f}" + "</p>"
    "<div style='border-top: 1px solid #334155; padding-top: 10px; margin-top: 8px;'>"
    "• <b>Entry (Köpzon):</b> " + f"{g_entry:.2f}" + " " + gazelle['valuta'] + " | <b>Target:</b> " + f"{g_target:.2f}" + " | <b>Stop-Loss:</b> " + f"{g_stop:.2f}" + "<br>"
    "• <b>Rekommenderad Positionsstorlek:</b> <b>" + str(g_shares) + " st aktier</b> (vid " + str(risk_pct) + "% portföljrisk)"
    "</div>"
    "</div>"
)
st.markdown(gazelle_html, unsafe_allow_html=True)
st.altair_chart(plot_neon_chart(gazelle["history"], "#eab308", 160), use_container_width=True)
