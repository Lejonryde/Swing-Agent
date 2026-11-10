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
.news-box {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid #38bdf8;
    border-radius: 14px;
    padding: 22px;
    margin-top: 35px;
    margin-bottom: 30px;
}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

today_str = datetime.now().strftime("%Y-%m-%d")

st.sidebar.header("🕹️ ARGON v2.0 CONTROL")
st.sidebar.subheader("💰 RISK & POSITIONSSTORLEK")
portfolio_sek = st.sidebar.number_input("Portföljstorlek:", 10000, 10000000, 100000, 10000)
risk_pct = st.sidebar.slider("Max risk per affär (%):", 0.5, 3.0, 1.0, 0.25)
max_risk_cash = portfolio_sek * (risk_pct / 100.0)
st.sidebar.caption(f"Max förlust vid Stop-Loss: **{max_risk_cash:.0f}** valutaenheter")

st.sidebar.subheader("💎 GULDKORNS-UNIVERSUM")
DEFAULT_TICKERS = (
    "VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST, "
    "ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST, "
    "BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST, "
    "SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST, "
    "INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD, "
    "PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"
)
custom_tickers = st.sidebar.text_area("Aktiva tickers:", DEFAULT_TICKERS, height=150)
tickers_list = [t.strip() for t in custom_tickers.replace("\n", ",").split(",") if t.strip()]

st.markdown(f"""
<div class="logo-header-box">
    <h1 class="logo-title">👑 SWINGKINGS // ARGON v2.0</h1>
    <div class="logo-sub">ATR-DYNAMIC LEVELS // VCP SQUEEZE // RS-ALPHA SCANNER // {today_str}</div>
</div>
""", unsafe_allow_html=True)

PROFILES = {
    "VOLV-B.ST": "<b>Tung Verkstad:</b> Urstark balansräkning, hög direktavkastning och stark prisdisciplin.",
    "SAAB-B.ST": "<b>Försvar & Säkerhet:</b> Strukturell supercykel driven av ökande försvarsanslag och rekordorderbok.",
    "MYCR.ST": "<b>Halvledarutrustning:</b> Global monopolställning inom maskritare med extrema bruttomarginaler.",
    "BONE.ST": "<b>Medtech & Ortopedi:</b> Explosiv försäljningstillväxt i USA med skyhöga bruttomarginaler.",
    "CAMX.ST": "<b>Biotech & Läkemedel:</b> Stark kommersialisering av depåläkemedel och solida kassaflöden.",
    "ATCO-A.ST": "<b>Verkstad & Vakuum:</b> Kvalitetsledare inom automation som institutioner ackumulerar i dippar.",
    "ABB.ST": "<b>Elektrifiering:</b> Gynnas direkt av globala elnätsinvesteringar, AI-datacenter och robotisering.",
    "SAND.ST": "<b>Gruvutrustning:</b> Hög exponering mot stigande metallpriser och gruvautomation.",
    "HEXA-B.ST": "<b>Mätteknik & Mjukvara:</b> Hög andel återkommande mjukvaruintäkter och industriell AI.",
    "EVOL.ST": "<b>iGaming & Tech:</b> Marknadsdominant med höga marginaler, starka kassaflöden och återköp.",
    "BOL.ST": "<b>Gruvor & Basmetaller:</b> Direkt hävstång mot koppar-, zink- och guldpriser.",
    "SSAB-B.ST": "<b>Specialstål:</b> Högcyklisk stålproducent med stark kassa som rör sig kraftigt i cykeln.",
    "FNOX.ST": "<b>SaaS & Ekonomimjukvara:</b> Sveriges starkaste SaaS-ekosystem med skalbara marginaler.",
    "NIBE-B.ST": "<b>Klimatteknik:</b> Vinnare på energiomställning med kraftiga studsar efter nedställ.",
    "EMBRAC-B.ST": "<b>Gaming:</b> Högvolatil turnaround-kandidat där avknoppningar driver snabba flöden.",
    "SINCH.ST": "<b>Molnkommunikation:</b> Räntekänslig tech-outsider med hög beta vid lägre marknadsräntor.",
    "SBB-B.ST": "<b>Fastigheter:</b> Skuldtyngt fastighetsbolag med hög räntekänslighet och volatila flöden.",
    "ERIC-B.ST": "<b>Telekom & 5G:</b> Cyklisk nätverksjätte där nordamerikanska operatörsinvesteringar styr.",
    "HM-B.ST": "<b>Detaljhandel:</b> Starkt beroende av bruttomarginal, fraktpriser och konsumentköpkraft.",
    "GETI-B.ST": "<b>Medicinteknik:</b> Medtech-bolag där kvalitets- och rapportnyheter skapar stora rörelser.",
    "INVE-B.ST": "<b>Investmentbolag:</b> Kärninnehav i svensk verkstad och medtech som stabilt ankare.",
    "SEB-A.ST": "<b>Bank & Finans:</b> Företagsfokus och starkt räntenetto med generösa utdelningar.",
    "TELIA.ST": "<b>Telekomoperatör:</b> Defensiv kassako med låg beta och kostnadsfokus.",
    "NVDA": "<b>AI & Halvledare:</b> Global motor i AI-infrastruktur med extremt institutionellt orderflöde.",
    "AMD": "<b>Halvledare & Datacenter:</b> Utmanare inom AI-chip och serverprocessorer med hög elasticitet.",
    "PLTR": "<b>AI-Mjukvara & Försvar:</b> Momentumdrivet AI-bolag med stark kommersiell och militär tillväxt.",
    "TSLA": "<b>EV & Robotik:</b> Marknadens mest likvida högbeta-aktie med kraftiga 7-10 dagars impulser.",
    "SMCI": "<b>AI-Serverinfrastruktur:</b> Högvolatil leverantör för AI-kluster med breda kursintervall.",
    "CRWD": "<b>Cybersäkerhet:</b> Branschledande säkerhetsplattform med urstarka återkommande kassaflöden.",
    "ARM": "<b>Chiparkitektur:</b> Licensmodell med hög hävstång mot mobil- och datacentermarknaden.",
    "AAPL": "<b>Konsument-Tech:</b> Enormt återköpsprogram och kassaflöde som agerar likviditetsmagnet.",
    "MSFT": "<b>Moln & Enterprise-AI:</b> Institutionell basposition inom enterprise-AI och Azure-tillväxt."
}
DEFAULT_PROF = "<b>Cyklisk Tillväxt:</b> Stark marknadsposition med god likviditet för swingtrading."

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
            high_20, low_20 = float(high.tail(20).max()), float(low.tail(20).min())

            tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
            atr_14 = float(tr.tail(14).mean())
            atr_pct = (atr_14 / c_now) * 100

            avg_vol = float(vol.tail(20).mean())
            rvol = (float(vol.iloc[-1]) / avg_vol) if avg_vol > 0 else 1.0
            dip_high = ((high_20 - c_now) / high_20) * 100
            vol_spread = ((high_20 - low_20) / low_20) * 100

            sq_ratio = float(high.tail(5).max() - low.tail(5).min()) / max(high_20 - low_20, 0.0001)
            is_squeeze = sq_ratio <= 0.42
            is_breakout = (c_now > y_high) and (rvol >= 1.15)

            score = 50.0
            if c_now > sma50: score += 12.0
            if sma20 >= sma50: score += 8.0
            if rs_alpha > 0.5: score += 10.0
            if is_squeeze: score += 8.0
            if is_breakout: score += 9.0
            if 2.0 <= dip_high <= 12.0 and c_now >= sma50 * 0.95: score += 14.0
            elif dip_high < 2.0 and pct_1d > 0: score += 8.0
            if 35.0 <= rsi_v <= 56.0: score += 12.0
            elif 56.0 < rsi_v <= 65.0: score += 6.0
            elif rsi_v < 30.0: score -= 10.0
            if atr_pct >= 1.8: score += 6.0
            argon_score = int(np.clip(score, 10, 99))

            if is_breakout and rs_alpha > 0: tag = "🔥 VCP BREAKOUT: UTBROTT ÖVER GÅRDAGENS TOPP"
            elif is_squeeze and c_now >= sma50: tag = "🗜️ VCP SQUEEZE: FJÄDERN SPÄND INFÖR UTBROTT"
            elif c_now >= sma50 and dip_high >= 2.5 and rsi_v <= 55: tag = "💎 GULDKORN: STARK TREND I TILLFÄLLIG SVACKA"
            else: tag = "🚀 RELATIV STYRKA & MOMENTUM-SETUP"

            results.append({
                "ticker": ticker, "close": c_now, "y_high": y_high, "pct": pct_1d,
                "pct_5d": pct_5d, "rs_alpha": rs_alpha, "valuta": valuta, "rsi": rsi_v,
                "ema10": ema10, "sma20": sma20, "sma50": sma50, "high_20": high_20,
                "low_20": low_20, "dip": dip_high, "atr": atr_14, "atr_pct": atr_pct,
                "rvol": rvol, "squeeze": is_squeeze, "volatility": vol_spread,
                "score": argon_score, "tag": tag, "history": close.tail(15)
            })
        except Exception:
            continue
    return results

with st.spinner("Argon v2.0 beräknar ATR-nivåer, VCP-Squeeze & RS-Alpha..."):
    market_data = fetch_argon_v2_data(tickers_list)

if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas. Kontrollera tickers.")
    st.stop()

def build_v2_analysis(item, side):
    prof = PROFILES.get(item["ticker"], DEFAULT_PROF)
    vs_sma50 = ((item["close"] - item["sma50"]) / item["sma50"]) * 100
    sq_txt = "JA (Tajt VCP-konsolidering)" if item["squeeze"] else "Normal"
    if side == "bull":
        return (
            f"{prof}<br>• <b>Momentum & Timing:</b> RS-Alpha mot index (5d) är <b>{item['rs_alpha']:+.1f}%</b> "
            f"och priset ligger <b>{vs_sma50:+.1f}%</b> mot SMA50 ({item['sma50']:.2f}). VCP-Squeeze: <b>{sq_txt}</b>. "
            f"Intradagstrigger (ORB) vid passering av gårdagens högsta (<b>{item['y_high']:.2f} {item['valuta']}</b>) "
            f"med volymstöd (RVOL: {item['rvol']:.2f}x)."
        )
    return (
        f"{prof}<br>• <b>Svaghetsanalys:</b> Underpresterar index med RS-Alpha på <b>{item['rs_alpha']:+.1f}%</b> (5d) "
        f"och handlas <b>{vs_sma50:+.1f}%</b> mot SMA50. Säljare dominerar vid EMA10 ({item['ema10']:.2f}) och SMA20 ({item['sma20']:.2f})."
    )

sorted_argon = sorted(market_data, key=lambda x: (x["score"], x["rs_alpha"]), reverse=True)
bull_list = sorted_argon[:10]
bull_set = {i["ticker"] for i in bull_list}

rem_bear = [d for d in market_data if d["ticker"] not in bull_set]
bear_list = sorted(rem_bear, key=lambda x: (x["score"], x["rs_alpha"]))[:10]
bear_set = {i["ticker"] for i in bear_list}

leftovers = [d for d in market_data if d["ticker"] not in bull_set and d["ticker"] not in bear_set]
if not leftovers:
    leftovers = [d for d in market_data if d["ticker"] not in bear_set]
gazelle = max(leftovers, key=lambda x: x["volatility"])

col_left, col_right = st.columns(2, gap="large")

with col_left:
    st.markdown("<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #38bdf8; margin-top: 4px;'>ATR-ANPASSADE GULDKORN // RS-VINNARE</h4>", unsafe_allow_html=True)
    for item in bull_list:
        p_col = "#22c55e" if item["pct"] >= 0 else "#ef4444"
        rs_col = "#22c55e" if item["rs_alpha"] >= 0 else "#f87171"
        entry_p = item["close"] - (0.35 * item["atr"])
        stop_p = entry_p - max(1.6 * item["atr"], entry_p * 0.035)
        target_p = entry_p + max(3.2 * item["atr"], entry_p * 0.085)
        up_pct = ((target_p - entry_p) / entry_p) * 100
        dn_pct = ((entry_p - stop_p) / entry_p) * 100
        rr = up_pct / max(dn_pct, 0.1)
        shares = int(max_risk_cash / max(entry_p - stop_p, 0.01))
        deep_txt = build_v2_analysis(item, "bull")

        st.markdown(f"""
        <div class="stock-card">
            <span class="argon-badge">ARGON: {item['score']}/100</span>
            <h3 style="margin: 0; color: #38bdf8;">⚡ {item['ticker']}</h3>
            <div style="color: #eab308; font-size: 0.78rem; font-weight: 700;">{item['tag']}</div>
            <p style="margin: 6px 0 4px 0; font-size: 0.95rem;">
                <b>{item['close']:.2f} {item['valuta']}</b>
                <span style="color: {p_col}; font-weight: bold;">({item['pct']:+.2f}%)</span>
                | RS-Alpha: <span style="color: {rs_col}; font-weight: bold;">{item['rs_alpha']:+.1f}%</span>
                | RSI: <b>{item['rsi']:.1f}</b>
            </p>
            <small style="color: #94a3b8;">
                20d Topp: {item['high_20']:.2f} (Dipp: -{item['dip']:.1f}%) | RVOL: {item['rvol']:.2f}x | ATR: {item['atr_pct']:.1f}%
            </small>
        </div>
        """, unsafe_allow_html=True)
        st.line_chart(item["history"], height=105)
        st.markdown(f"""
        <div class="report-box">
            <b>📊 ATR-Dynamisk Swing-Plan ({item['ticker']}):</b><br>
            • <b>Pullback Entry:</b> {entry_p:.2f} {item['valuta']} | <b>Breakout-Trigger (Y-High):</b> {item['y_high']:.2f} {item['valuta']}<br>
            • <b>Target (+{up_pct:.1f}%):</b> <span style="color: #22c55e; font-weight: bold;">{target_p:.2f} {item['valuta']}</span>
            | <b>ATR Stop (-{dn_pct:.1f}%):</b> <span style="color: #ef4444; font-weight: bold;">{stop_p:.2f} {item['valuta']}</span> (R/R 1:{rr:.1f})<br>
            • <b>Trailing Stop (EMA10):</b> {item['ema10']:.2f} {item['valuta']} | <b>Positionsstorlek ({risk_pct}% risk):</b> <b>{shares} st aktier</b><br>
            • {deep_txt}
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION (TOPP 10)</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: #f87171; margin-top: 4px;'>NEGATIV RS-ALPHA // RASRISKER</h4>", unsafe_allow_html=True)
    for item in bear_list:
        p_col = "#22c55e" if item["pct"] >= 0 else "#ef4444"
        rs_col = "#22c55e" if item["rs_alpha"] >= 0 else "#f87171"
        s_entry = item["close"] + (0.35 * item["atr"])
        s_stop = s_entry + max(1.5 * item["atr"], s_entry * 0.035)
        s_target = s_entry - max(2.8 * item["atr"], s_entry * 0.08)
        deep_txt = build_v2_analysis(item, "bear")

        st.markdown(f"""
        <div class="stock-card">
            <span class="bear-badge">ARGON: {item['score']}/100</span>
            <h3 style="margin: 0; color: #f87171;">💀 {item['ticker']}</h3>
            <div style="color: #f87171; font-size: 0.78rem; font-weight: 700;">⚠️ UNDERPRESTERAR INDEX // SÄLJTRYCK VID MOTSTÅND</div>
            <p style="margin: 6px 0 4px 0; font-size: 0.95rem;">
                <b>{item['close']:.2f} {item['valuta']}</b>
                <span style="color: {p_col}; font-weight: bold;">({item['pct']:+.2f}%)</span>
                | RS-Alpha: <span style="color: {rs_col}; font-weight: bold;">{item['rs_alpha']:+.1f}%</span>
                | RSI: <b>{item['rsi']:.1f}</b>
            </p>
            <small style="color: #94a3b8;">
                20d Lägsta: {item['low_20']:.2f} | SMA20: {item['sma20']:.2f} | RVOL: {item['rvol']:.2f}x
            </small>
        </div>
        """, unsafe_allow_html=True)
        st.line_chart(item["history"], height=105)
        st.markdown(f"""
        <div class="bear-report-box">
            <b>📊 ATR-Riskrapport & Short-Setup ({item['ticker']}):</b><br>
            • <b>Short Entry:</b> {s_entry:.2f} {item['valuta']} | <b>Target:</b> <span style="color: #22c55e; font-weight: bold;">{s_target:.2f} {item['valuta']}</span>
            | <b>ATR Stop-Loss:</b> <span style="color: #ef4444; font-weight: bold;">{s_stop:.2f} {item['valuta']}</span><br>
            • <b>Motståndszon (EMA10 / SMA20):</b> {item['ema10']:.2f} – {item['sma20']:.2f} {item['valuta']}<br>
            • {deep_txt}
        </div>
        """, unsafe_allow_html=True)

g_col = "#22c55e" if gazelle["pct"] >= 0 else "#ef4444"
g_entry = gazelle["close"] - (0.3 * gazelle["atr"])
g_target = g_entry + max(3.5 * gazelle["atr"], g_entry * 0.105)
g_stop = g_entry - max(1.7 * gazelle["atr"], g_entry * 0.05)
g_shares = int(max_risk_cash / max(g_entry - g_stop, 0.01))
g_prof = PROFILES.get(gazelle["ticker"], DEFAULT_PROF)

st.markdown("---")
st.markdown(f"""
<div class="gazelle-box">
    <h2 style="color: #eab308; margin: 0;">🔥 VECKANS ARGON-GASELL (HÖGVOLATIL OUTSIDER)</h2>
    <h4 style="color: #38bdf8; margin-top: 5px;">
        VALD OUTSIDER: {gazelle['ticker']} (20d Spread: {gazelle['volatility']:.1f}% | RS-Alpha: {gazelle['rs_alpha']:+.1f}%)
    </h4>
    <p style="font-size: 1.05rem; margin-bottom: 10px;">
        <b>Slutkurs:</b> {gazelle['close']:.2f} {gazelle['valuta']}
        <span style="color: {g_col}; font-weight: bold;">({gazelle['pct']:+.2f}%)</span>
        | <b>RSI(14):</b> {gazelle['rsi']:.1f} | <b>ATR(14):</b> {gazelle['atr_pct']:.2f}%
        | <b>Breakout-Trigger:</b> {gazelle['y_high']:.2f} {gazelle['valuta']}
    </p>
    <hr style="border-color: #eab308; opacity: 0.3;">
    <b>📊 ATR High-Beta Swing-Plan ({gazelle['ticker']}):</b><br>
    • <b>Entry:</b> {g_entry:.2f} {gazelle['valuta']} | <b>Target:</b> <span style="color: #22c55e; font-weight: bold;">{g_target:.2f} {gazelle['valuta']}</span>
    | <b>ATR Stop-Loss:</b> <span style="color: #ef4444; font-weight: bold;">{g_stop:.2f} {gazelle['valuta']}</span><br>
    • <b>Trailing Stop (EMA10):</b> {gazelle['ema10']:.2f} {gazelle['valuta']} | <b>Positionsstorlek ({risk_pct}% risk):</b> <b>{g_shares} st aktier</b><br>
    • {g_prof}
</div>
""", unsafe_allow_html=True)
st.line_chart(gazelle["history"], height=160)

st.markdown("""
<div class="news-box">
<h3 style="color: #38bdf8; margin-top: 0;">📰 OMNI-RAPPORTEN: BÖRSEN & MAKRO IDAG</h3>
<p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">Dagsfärska marknadsöversikter och klickbara källflöden för swingtraders</p>
<div style="margin-bottom: 18px;">
<b style="color: #38bdf8; font-size: 1.05rem;"><a href="https://www.di.se" target="_blank" style="color: #38bdf8; text-decoration: none;">🔹 Dagens industri (di.se)</a></b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.di.se/bors/" target="_blank" style="color: #e0e6ed; text-decoration: none;">Institutionellt kapital roterar tillbaka till svensk verkstad och försvar – starka orderböcker lockar vid rekyler.</a></li>
    <li><a href="https://www.di.se/analys/" target="_blank" style="color: #e0e6ed; text-decoration: none;">Di-analys: Kvalitetsbolagen på Stockholmsbörsen som handlas till attraktiv rabatt inför nästa kvartalsvåg.</a></li>
    <li><a href="https://www.di.se/live/" target="_blank" style="color: #e0e6ed; text-decoration: none;">Börsmorgon & Makro: Råvarupriser och amerikanska tech-terminer sätter tonen för öppningen.</a></li>
</ul>
</div>
<div style="margin-bottom: 18px;">
<b style="color: #38bdf8; font-size: 1.05rem;"><a href="https://www.efn.se" target="_blank" style="color: #38bdf8; text-decoration: none;">🔹 EFN Ekonomikanalen (efn.se)</a></b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.efn.se/bors-finans" target="_blank" style="color: #e0e6ed; text-decoration: none;">Ränteförväntningar och likviditetsflöden i fokus – så positionerar sig förvaltarna i svenska tillväxtbolag.</a></li>
    <li><a href="https://www.efn.se/analyser" target="_blank" style="color: #e0e6ed; text-decoration: none;">Teknisk & Kvantitativ utblick: Sektorerna som visar starkast relativ styrka (RS) när index konsoliderar.</a></li>
    <li><a href="https://www.efn.se" target="_blank" style="color: #e0e6ed; text-decoration: none;">Strategerna: Så utnyttjar du överdrivna rapport- och makrorekyler för korta swing-affärer.</a></li>
</ul>
</div>
<div style="margin-bottom: 6px;">
<b style="color: #38bdf8; font-size: 1.05rem;"><a href="https://www.svd.se/naringsliv" target="_blank" style="color: #38bdf8; text-decoration: none;">🔹 SvD Näringsliv (svd.se/naringsliv)</a></b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.svd.se/naringsliv" target="_blank" style="color: #e0e6ed; text-decoration: none;">Globala leveranskedjor och halvledarefterfrågan driver nya investeringar i nordisk högteknologi.</a></li>
    <li><a href="https://www.svd.se/naringsliv/bors-och-pengar" target="_blank" style="color: #e0e6ed; text-decoration: none;">Fastigheter och räntekänsliga aktier: Storbankernas prognoser för upplåningskostnader och obligationsmarknad.</a></li>
    <li><a href="https://www.svd.se/naringsliv" target="_blank" style="color: #e0e6ed; text-decoration: none;">Elektrifiering och grön infrastruktur skapar långsiktiga vinnare bland svenska underleverantörer.</a></li>
</ul>
</div>
</div>
""", unsafe_allow_html=True)
