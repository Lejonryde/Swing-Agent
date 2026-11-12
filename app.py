import os
import json
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="SWINGKINGS // ARGON v2.0", page_icon="👑", layout="wide")

CSS_LINES = [
    "<style>",
    "html, body, [data-testid='stAppViewContainer'] { background: linear-gradient(135deg, #05070b, #0a0e17, #0f172a) !important; color: #e2e8f0 !important; background-attachment: fixed; }",
    "[data-testid='stSidebar'] { background-color: #090d14 !important; border-right: 1px solid #1e293b !important; }",
    ".logo-header-box { background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; box-shadow: 0 0 35px rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 24px; margin-bottom: 25px; text-align: center; }",
    ".logo-title { font-size: 2.8rem; font-weight: 900; letter-spacing: 3px; background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }",
    ".logo-sub { color: #94a3b8; font-size: 0.88rem; letter-spacing: 2px; margin-top: 8px; text-transform: uppercase; }",
    ".stock-card { background: rgba(17, 24, 39, 0.92); border: 1px solid #334155; border-radius: 12px; padding: 15px; margin-bottom: 10px; }",
    ".argon-badge { background: linear-gradient(90deg, #0284c7, #2563eb); color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; float: right; }",
    ".bear-badge { background: linear-gradient(90deg, #dc2626, #991b1b); color: #ffffff; padding: 3px 10px; border-radius: 6px; font-size: 0.78rem; font-weight: 700; float: right; }",
    ".gazelle-badge { background: linear-gradient(90deg, #eab308, #ca8a04); color: #000000; padding: 4px 12px; border-radius: 6px; font-size: 0.82rem; font-weight: 800; float: right; }",
    ".report-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #38bdf8; border-left: 5px solid #38bdf8; border-radius: 8px; padding: 12px 16px; margin: 6px 0 12px 0; font-size: 0.88rem; line-height: 1.55; }",
    ".bear-report-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #ef4444; border-left: 5px solid #ef4444; border-radius: 8px; padding: 12px 16px; margin: 6px 0 12px 0; font-size: 0.88rem; line-height: 1.55; }",
    ".gazelle-box { background: rgba(15, 23, 42, 0.96); border: 2px solid #eab308; box-shadow: 0 0 25px rgba(234, 179, 8, 0.25); border-radius: 14px; padding: 22px; margin: 30px 0 15px 0; line-height: 1.6; }",
    ".sim-box { background: rgba(15, 23, 42, 0.94); border: 1px solid #10b981; border-left: 5px solid #10b981; border-radius: 10px; padding: 18px; margin-bottom: 20px; }",
    "</style>"
]
st.markdown("\n".join(CSS_LINES), unsafe_allow_html=True)

today_dt = datetime.now()
today_str = today_dt.strftime("%Y-%m-%d %H:%M")

st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
fiktiv_kassa = st.sidebar.number_input("Fiktiv Startkassa (SEK):", 10000, 1000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)
hold_days = st.sidebar.slider("Mål-innehavstid (dagar):", 3, 20, 8, 1)

PORTFOLIO_FILE = "paper_portfolio.json"

def load_portfolio(initial_cash):
    if os.path.exists(PORTFOLIO_FILE):
        try:
            with open(PORTFOLIO_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"cash": float(initial_cash), "initial_cash": float(initial_cash), "positions": [], "history": []}

def save_portfolio(data):
    try:
        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

if st.sidebar.button("🔄 Nollställ Paper-Portfölj"):
    if os.path.exists(PORTFOLIO_FILE):
        os.remove(PORTFOLIO_FILE)
    st.rerun()

DEFAULT_TICKERS = "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=120)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(
    "<div class='logo-header-box'>"
    "<h1 class='logo-title'>👑 SWINGKINGS // ARGON v2.0</h1>"
    "<div class='logo-sub'>LOCKED PAPER TRADING // MAX 10% TARGET // AUTO-EVALUATION (1H) // " + today_str + "</div>"
    "</div>",
    unsafe_allow_html=True
)

@st.cache_data(ttl=3600)
def fetch_argon_v2_data(tickers):
    omx_5d, spx_5d = 0.0, 0.0
    try:
        omx = yf.Ticker("^OMX").history(period="1mo").dropna()
        if len(omx) >= 6:
            omx_5d = ((float(omx["Close"].iloc[-1]) - float(omx["Close"].iloc[-6])) / float(omx["Close"].iloc[-6])) * 100
    except Exception:
        pass
    try:
        spx = yf.Ticker("^GSPC").history(period="1mo").dropna()
        if len(spx) >= 6:
            spx_5d = ((float(spx["Close"].iloc[-1]) - float(spx["Close"].iloc[-6])) / float(spx["Close"].iloc[-6])) * 100
    except Exception:
        pass

    results = []
    for ticker in tickers:
        try:
            df = yf.Ticker(ticker).history(period="3mo").dropna(subset=["Close", "High", "Low"])
            if df.empty or len(df) < 20:
                continue
            close, high, low = df["Close"], df["High"], df["Low"]
            c_now, c_prev = float(close.iloc[-1]), float(close.iloc[-2])
            h_today, l_today = float(high.iloc[-1]), float(low.iloc[-1])
            if np.isnan(c_now) or c_now <= 0:
                continue

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
            atr_raw = float(tr.tail(14).mean())
            atr_14 = atr_raw if (not np.isnan(atr_raw) and atr_raw > 0) else (c_now * 0.025)

            dip_high = ((high_20 - c_now) / high_20) * 100 if high_20 > 0 else 0.0
            low_20 = float(low.tail(20).min())
            vol_spread = ((high_20 - low_20) / low_20) * 100 if low_20 > 0 else 0.0

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
                "ticker": ticker, "close": c_now, "high_today": h_today, "low_today": l_today,
                "pct": pct_1d, "rs_alpha": rs_alpha, "valuta": valuta, "rsi": rsi_v,
                "atr": atr_14, "volatility": vol_spread, "score": argon_score, "history": hist_df
            })
        except Exception:
            continue
    return results

def plot_plotly_chart(hist_df, color_hex, fill_rgba, height=110):
    fig = px.line(hist_df, x="Datum", y="Pris", template="plotly_dark")
    fig.update_traces(line=dict(color=color_hex, width=2.5), fill="tozeroy", fillcolor=fill_rgba, mode="lines")
    min_y = float(hist_df["Pris"].min()) * 0.985
    max_y = float(hist_df["Pris"].max()) * 1.015
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        margin=dict(l=0, r=0, t=5, b=0),
        height=height,
        xaxis=dict(showgrid=False, zeroline=False, color="#94a3b8"),
        yaxis=dict(showgrid=True, gridcolor="#1e293b", zeroline=False, color="#94a3b8", range=[min_y, max_y])
    )
    return fig

def calc_capped_levels(price, atr):
    raw_target = price + (2.5 * atr)
    target = min(max(raw_target, price * 1.065), price * 1.10)
    raw_stop = price - (1.4 * atr)
    stop = max(min(raw_stop, price * 0.97), price * 0.955)
    return target, stop

def safe_shares(cash, risk, entry, stop):
    try:
        diff = max(float(entry) - float(stop), 0.01)
        val = (float(cash) * (float(risk) / 100.0)) / diff
        if np.isnan(val) or np.isinf(val):
            return 1
        return max(int(val), 1)
    except Exception:
        return 1

market_data = fetch_argon_v2_data(tickers_list)
if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas.")
    st.stop()

market_map = {item["ticker"]: item for item in market_data}
sorted_argon = sorted(market_data, key=lambda x: (x["score"], x["rs_alpha"]), reverse=True)
bull_list = sorted_argon[:10]
bull_set = {i["ticker"] for i in bull_list}
bear_list = sorted([d for d in market_data if d["ticker"] not in bull_set], key=lambda x: (x["score"], x["rs_alpha"]))[:10]
bear_set = {i["ticker"] for i in bear_list}
gazelle = max([d for d in market_data if d["ticker"] not in bull_set and d["ticker"] not in bear_set] or market_data, key=lambda x: x["volatility"])

portfolio = load_portfolio(fiktiv_kassa)
active_positions = []
fx_rate = 10.80

for pos in portfolio["positions"]:
    tkr = pos["ticker"]
    ent_p = float(pos["entry_price"])

    # Tvinga ned eventuella gamla överhöga Target/Stop-nivåer på befintliga positioner
    pos["target"] = min(max(float(pos["target"]), ent_p * 1.065), ent_p * 1.10)
    pos["stop"] = max(min(float(pos["stop"]), ent_p * 0.97), ent_p * 0.955)

    if tkr in market_map:
        m = market_map[tkr]
        cur_p = m["close"]
        h_p = m["high_today"]
        l_p = m["low_today"]
    else:
        cur_p = ent_p
        h_p = cur_p
        l_p = cur_p

    entry_dt = datetime.strptime(pos["entry_date"], "%Y-%m-%d")
    days_held = (today_dt - entry_dt).days
    planned_exit_dt = datetime.strptime(pos["planned_exit"], "%Y-%m-%d")

    sell_reason = None
    exit_price = cur_p

    if l_p <= pos["stop"]:
        sell_reason = "🛑 STOP-LOSS NÅDD"
        exit_price = pos["stop"]
    elif h_p >= pos["target"]:
        sell_reason = "🎯 TARGET NÅDD (VINSTHEMTAKNING)"
        exit_price = pos["target"]
    elif today_dt >= planned_exit_dt or days_held >= hold_days:
        sell_reason = "⏰ TIDSGRÄNS (" + str(hold_days) + " DAGAR)"
        exit_price = cur_p

    if sell_reason:
        roi_pct = ((exit_price - ent_p) / ent_p) * 100.0
        returned_sek = pos["allocated_sek"] * (1.0 + (roi_pct / 100.0))
        profit_sek = returned_sek - pos["allocated_sek"]
        portfolio["cash"] += returned_sek
        portfolio["history"].append({
            "Ticker": tkr,
            "Entry-datum": pos["entry_date"],
            "Exit-datum": today_dt.strftime("%Y-%m-%d"),
            "Entrykurs": round(ent_p, 2),
            "Exitkurs": round(exit_price, 2),
            "Avkastning (%)": round(roi_pct, 2),
            "Resultat (SEK)": round(profit_sek, 0),
            "Orsak": sell_reason
        })
    else:
        pos["current_price"] = cur_p
        pos["days_held"] = days_held
        active_positions.append(pos)

portfolio["positions"] = active_positions

open_slots = 3 - len(portfolio["positions"])
if open_slots > 0 and portfolio["cash"] > 1000:
    held_tickers = {p["ticker"] for p in portfolio["positions"]}
    candidates = [b for b in bull_list if b["ticker"] not in held_tickers]
    for cand in candidates[:open_slots]:
        alloc_sek = portfolio["cash"] / open_slots
        c_price = cand["close"]
        t_target, t_stop = calc_capped_levels(c_price, cand["atr"])
        conv = fx_rate if cand["valuta"] == "USD" else 1.0
        shares = max(int((alloc_sek / conv) / c_price), 1) if c_price > 0 else 1

        new_pos = {
            "ticker": cand["ticker"],
            "valuta": cand["valuta"],
            "entry_price": c_price,
            "current_price": c_price,
            "target": t_target,
            "stop": t_stop,
            "shares": shares,
            "allocated_sek": alloc_sek,
            "entry_date": today_dt.strftime("%Y-%m-%d"),
            "planned_exit": (today_dt + timedelta(days=hold_days)).strftime("%Y-%m-%d"),
            "days_held": 0
        }
        portfolio["positions"].append(new_pos)
        portfolio["cash"] -= alloc_sek
        open_slots -= 1

save_portfolio(portfolio)

active_value_sek = 0.0
for p in portfolio["positions"]:
    p_roi = ((p["current_price"] - p["entry_price"]) / p["entry_price"])
    active_value_sek += p["allocated_sek"] * (1.0 + p_roi)

total_portfolio_sek = portfolio["cash"] + active_value_sek
base_cash = portfolio.get("initial_cash", fiktiv_kassa)
total_roi_pct = ((total_portfolio_sek - base_cash) / base_cash) * 100.0
tot_color = "#10b981" if total_roi_pct >= 0 else "#ef4444"

st.markdown(
    "<div class='sim-box'>"
    "<h3 style='color: #10b981; margin: 0 0 10px 0;'>📊 LÅST PAPER TRADING & PORTFÖJ-SIMULATOR</h3>"
    "<p style='margin: 0; line-height: 1.6;'>"
    "<b>Totalt Portföljvärde:</b> " + f"{total_portfolio_sek:,.0f}" + " SEK "
    "(<span style='color: " + tot_color + "; font-weight: bold;'>" + f"{total_roi_pct:+.2f}%" + "</span>) | "
    "<b>Fri Kassa:</b> " + f"{portfolio['cash']:,.0f}" + " SEK | "
    "<b>Låsta Innehav:</b> " + str(len(portfolio["positions"])) + "/3 st | "
    "<b>Regel:</b> Target begränsad till +6,5% till +10,0% (Stop -3,0% till -4,5%)."
    "</p>"
    "</div>",
    unsafe_allow_html=True
)

sim_cols = st.columns(3)
for idx, pos in enumerate(portfolio["positions"]):
