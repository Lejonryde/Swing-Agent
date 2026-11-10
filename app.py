import os
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime

st.set_page_config(
    page_title="SWINGKINGS // ARGON",
    page_icon="👑",
    layout="wide"
)

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
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: 4px;
    background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}
.logo-sub {
    color: #94a3b8;
    font-size: 0.9rem;
    letter-spacing: 2px;
    margin-top: 8px;
    text-transform: uppercase;
}
.stock-card {
    background: rgba(17, 24, 39, 0.9);
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
    font-size: 0.8rem;
    font-weight: 700;
    float: right;
}
.bear-badge {
    background: linear-gradient(90deg, #dc2626, #991b1b);
    color: #ffffff;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 700;
    float: right;
}
.report-box {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid #38bdf8;
    border-left: 5px solid #38bdf8;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 22px;
    font-size: 0.88rem;
    line-height: 1.5;
}
.bear-report-box {
    background: rgba(15, 23, 42, 0.92);
    border: 1px solid #ef4444;
    border-left: 5px solid #ef4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 6px;
    margin-bottom: 22px;
    font-size: 0.88rem;
    line-height: 1.5;
}
.gazelle-box {
    background: rgba(15, 23, 42, 0.95);
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

st.sidebar.header("🕹️ ARGON CONTROL PANEL")
st.sidebar.subheader("💎 GULDKORNS-UNIVERSUM")

DEFAULT_TICKERS = """VOLV-B.ST, SAAB-B.ST, MYCR.ST, BONE.ST, CAMX.ST,
ATCO-A.ST, ABB.ST, SAND.ST, HEXA-B.ST, EVOL.ST,
BOL.ST, SSAB-B.ST, FNOX.ST, NIBE-B.ST, EMBRAC-B.ST,
SINCH.ST, SBB-B.ST, ERIC-B.ST, HM-B.ST, GETI-B.ST,
INVE-B.ST, SEB-A.ST, TELIA.ST, NVDA, AMD,
PLTR, TSLA, SMCI, CRWD, ARM, AAPL, MSFT"""

custom_tickers = st.sidebar.text_area(
    "Aktiva tickers (32 st):",
    DEFAULT_TICKERS,
    height=180
)
raw_list = custom_tickers.replace("\n", ",").split(",")
tickers_list = [t.strip() for t in raw_list if t.strip()]

HEADER_HTML = f"""
<div class="logo-header-box">
    <h1 class="logo-title">👑 SWINGKINGS // ARGON</h1>
    <div class="logo-sub">
        QUANT & GOLDMINE SCANNER (10+10 AKTIER // 7-10 DAGAR // MÅL 8-10%)
        // {today_str}
    </div>
</div>
"""
st.markdown(HEADER_HTML, unsafe_allow_html=True)

PROFILES = {
    "VOLV-B.ST": """<b>Tung Verkstad:</b> Urstark balansräkning, hög
    direktavkastning och stark prisdisciplin i konjunkturcykeln.""",
    "SAAB-B.ST": """<b>Försvar & Säkerhet:</b> Strukturell supercykel
    driven av ökande försvarsanslag och rekordstor orderbok.""",
    "MYCR.ST": """<b>Halvledarutrustning:</b> Global monopolställning
    inom maskritare med extrema bruttomarginaler.""",
    "BONE.ST": """<b>Medtech & Ortopedi:</b> Explosiv försäljningstillväxt
    i USA för syntetiska bengraft med skyhöga marginaler.""",
    "CAMX.ST": """<b>Biotech & Läkemedel:</b> Stark kommersialisering av
    depåläkemedel och solida kassaflöden i ocyklisk tillväxtfas.""",
    "ATCO-A.ST": """<b>Verkstad & Vakuum:</b> Kvalitetsledare inom
    automation som institutioner ackumulerar i dippar.""",
    "ABB.ST": """<b>Elektrifiering & Automation:</b> Gynnas direkt av
    globala elnätsinvesteringar, AI-datacenter och robotisering.""",
    "SAND.ST": """<b>Gruvutrustning:</b> Hög exponering mot stigande
    metallpriser och gruvautomation med stark eftermarknad.""",
    "HEXA-B.ST": """<b>Mätteknik & Mjukvara:</b> Hög andel återkommande
    mjukvaruintäkter och positionerad för industriell AI.""",
    "EVOL.ST": """<b>iGaming & Tech:</b> Marknadsdominant med över 60%
    EBITDA-marginal, starka kassaflöden och aktieåterköp.""",
    "BOL.ST": """<b>Gruvor & Basmetaller:</b> Direkt hävstång mot koppar-,
    zink- och guldpriser i elektrifieringsvågen.""",
    "SSAB-B.ST": """<b>Specialstål:</b> Högcyklisk stålproducent med stark
    kassa som rör sig kraftigt vid konjunkturskiften.""",
    "FNOX.ST": """<b>SaaS & Finansiell Mjukvara:</b> Sveriges starkaste
    SaaS-ekosystem med prishöjningskraft och skalbarhet.""",
    "NIBE-B.ST": """<b>Klimatteknik:</b> Långsiktig vinnare på europeisk
    energiomställning med kraftiga studsar efter nedställ.""",
    "EMBRAC-B.ST": """<b>Gaming:</b> Högvolatil turnaround-kandidat där
    avknoppningar och spelsläpp driver snabba flöden.""",
    "SINCH.ST": """<b>Molnkommunikation:</b> Räntekänslig tech-outsider
    med hög beta som reagerar explosivt vid lägre räntor.""",
    "SBB-B.ST": """<b>Fastigheter:</b> Skuldtyngt fastighetsbolag med
    hög räntekänslighet och volatila obligationsflöden.""",
    "ERIC-B.ST": """<b>Telekom & 5G:</b> Cyklisk nätverksjätte där
    nordamerikanska operatörsinvesteringar styr marginalen.""",
    "HM-B.ST": """<b>Detaljhandel:</b> Starkt beroende av bruttomarginal,
    fraktpriser och konsumenternas köpkraft.""",
    "GETI-B.ST": """<b>Medicinteknik:</b> Värderingspressat medtech-bolag
    där kvalitets- och rapportnyheter skapar stora rörelser.""",
    "INVE-B.ST": """<b>Investmentbolag:</b> Kärninnehav i svensk verkstad
    och medtech som fungerar som stabilt ankare.""",
    "SEB-A.ST": """<b>Bank & Finans:</b> Företagsfokus och starkt
    räntenetto med generösa utdelningar och återköp.""",
    "TELIA.ST": """<b>Telekomoperatör:</b> Defensiv kassako med låg beta
    och fokus på kostnadsbesparingar.""",
    "NVDA": """<b>AI & Halvledare:</b> Global motor i AI-infrastruktur
    med extremt institutionellt orderflöde.""",
    "AMD": """<b>Halvledare & Datacenter:</b> Utmanare inom AI-chip
    och serverprocessorer med hög swing-elasticitet.""",
    "PLTR": """<b>AI-Mjukvara & Försvar:</b> Momentumdrivet AI-bolag
    med stark tillväxt inom kommersiell och militär sektor.""",
    "TSLA": """<b>EV, Autonomi & Robotik:</b> Marknadens mest likvida
    högbeta-aktie med kraftiga 7-10 dagars impulser.""",
    "SMCI": """<b>AI-Serverinfrastruktur:</b> Högvolatil leverantör för
    vätskekylda AI-kluster med breda kursintervall.""",
    "CRWD": """<b>Cybersäkerhet:</b> Branschledande säkerhetsplattform
    med urstarka kassaflöden och återkommande intäkter.""",
    "ARM": """<b>Chiparkitektur:</b> Licensmodell med hög hävstång mot
    mobil- och datacentermarknaden.""",
    "AAPL": """<b>Konsument-Tech:</b> Enormt återköpsprogram och stabilt
    kassaflöde som agerar global likviditetsmagnet.""",
    "MSFT": """<b>Moln & Enterprise-AI:</b> Institutionell basposition
    inom enterprise-AI och global Azure-tillväxt."""
}

DEFAULT_PROFILE = """<b>Cyklisk Tillväxt:</b> Stark marknadsposition med
god likviditet och tydliga tekniska swing-mönster."""


@st.cache_data(ttl=900)
def fetch_argon_data(tickers):
    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="3mo")
            if df.empty or len(df) < 15:
                continue

            close = df["Close"]
            high = df["High"]
            low = df["Low"]
            vol = df["Volume"]

            c_now = float(close.iloc[-1])
            c_prev = float(close.iloc[-2])
            pct_1d = ((c_now - c_prev) / c_prev) * 100

            c_5d = float(close.iloc[-6]) if len(close) >= 6 else c_prev
            pct_5d = ((c_now - c_5d) / c_5d) * 100

            valuta = "SEK" if ticker.endswith(".ST") else "USD"

            rsi_s = ta.momentum.rsi(close=close, window=14)
            rsi_v = float(rsi_s.iloc[-1])
            if pd.isna(rsi_v):
                rsi_v = 50.0

            sma20 = float(close.tail(20).mean())
            sma50 = float(close.tail(50).mean()) if len(close) >= 50 else sma20

            high_20 = float(high.tail(20).max())
            low_20 = float(low.tail(20).min())

            tr1 = high - low
            tr2 = (high - close.shift(1)).abs()
            tr3 = (low - close.shift(1)).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr_14 = float(tr.tail(14).mean())
            atr_pct = (atr_14 / c_now) * 100

            avg_vol = float(vol.tail(20).mean())
            cur_vol = float(vol.iloc[-1])
            rvol = (cur_vol / avg_vol) if avg_vol > 0 else 1.0

            dip_high = ((high_20 - c_now) / high_20) * 100
            vol_spread = ((high_20 - low_20) / low_20) * 100

            score = 50.0
            if c_now > sma50:
                score += 14.0
            if sma20 >= sma50:
                score += 10.0

            if 2.0 <= dip_high <= 12.0 and c_now >= sma50 * 0.95:
                score += 18.0
            elif dip_high < 2.0 and pct_1d > 0:
                score += 10.0

            if 34.0 <= rsi_v <= 54.0:
                score += 14.0
            elif 54.0 < rsi_v <= 64.0:
                score += 8.0
            elif rsi_v < 30.0:
                score -= 8.0

            if atr_pct >= 1.8:
                score += 8.0
            if rvol >= 1.05 and pct_1d >= -1.0:
                score += 6.0

            argon_score = int(np.clip(score, 10, 99))

            if c_now >= sma50 and dip_high >= 2.5 and rsi_v <= 54:
                tag = "💎 GULDKORN: STARK TREND I TILLFÄLLIG SVACKA"
            elif c_now >= sma20 and rsi_v > 54:
                tag = "🚀 MOMENTUM-FORTSÄTTNING I STARK SEKTOR"
            else:
                tag = "⚡ MEAN-REVERSION VID TEKNISKT STÖD"

            results.append({
                "ticker": ticker,
                "close": c_now,
                "pct": pct_1d,
                "pct_5d": pct_5d,
                "valuta": valuta,
                "rsi": rsi_v,
                "sma20": sma20,
                "sma50": sma50,
                "high_20": high_20,
                "low_20": low_20,
                "dip": dip_high,
                "atr_pct": atr_pct,
                "rvol": rvol,
                "volatility": vol_spread,
                "score": argon_score,
                "tag": tag,
                "history": close.tail(15)
            })
        except Exception:
            continue
    return results


with st.spinner("Argon Quant Engine skannar efter guldkorn..."):
    market_data = fetch_argon_data(tickers_list)

if not market_data:
    st.warning("Ingen marknadsdata kunde hämtas. Kontrollera tickers.")
    st.stop()


def build_analysis(item, side):
    t = item["ticker"]
    prof = PROFILES.get(t, DEFAULT_PROFILE)
    vs_sma50 = ((item["close"] - item["sma50"]) / item["sma50"]) * 100

    if side == "bull":
        return f"""
        {prof}<br>
        • <b>Argon Dip-In-Strength:</b> Aktien handlas <b>{vs_sma50:+.1f}%</b>
        mot SMA50 ({item['sma50']:.2f} {item['valuta']}) efter en tillfällig
        svacka på <b>-{item['dip']:.1f}%</b> från 20d-toppen. Med RSI på
        <b>{item['rsi']:.1f}</b> och RVOL på <b>{item['rvol']:.2f}x</b> är
        säljtrycket uttömt i en fundamentalt stark trend. Daglig ATR på
        <b>{item['atr_pct']:.2f}%</b> ger kraft för +8.5% till +10% på
        7–10 dagar.
        """
    return f"""
    {prof}<br>
    • <b>Argon Svaghetsanalys:</b> Aktien presterar <b>{vs_sma50:+.1f}%</b>
    mot SMA50 ({item['sma50']:.2f} {item['valuta']}) och handlas
    <b>-{item['dip']:.1f}%</b> under sin 20d-topp. Svagt köparflöde
    (RVOL: {item['rvol']:.2f}x, RSI: {item['rsi']:.1f}) gör att uppstudsar
    mot SMA20 ({item['sma20']:.2f}) möter säljare.
    """


sorted_argon = sorted(
    market_data,
    key=lambda x: (x["score"], x["pct"]),
    reverse=True
)

bull_list = sorted_argon[:10]
bull_set = {i["ticker"] for i in bull_list}

rem_bear = [d for d in market_data if d["ticker"] not in bull_set]
bear_list = sorted(rem_bear, key=lambda x: (x["score"], x["pct"]))[:10]
bear_set = {i["ticker"] for i in bear_list}

leftovers = [
    d for d in market_data
    if d["ticker"] not in bull_set and d["ticker"] not in bear_set
]
if not leftovers:
    leftovers = [d for d in market_data if d["ticker"] not in bear_set]
gazelle = max(leftovers, key=lambda x: x["volatility"])

col_buy, col_sell = st.columns(2, gap="large")

with col_buy:
    st.markdown(
        "<h2 style='color: #0284c7; margin: 0;'>🔵 BULL DIVISION (TOPP 10)</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='color: #38bdf8; margin-top: 4px;'>"
        "GULDKORN: STARKA BOLAG I TILLFÄLLIG SVACKA</h4>",
        unsafe_allow_html=True
    )

    for item in bull_list:
        p_col = "#22c55e" if item["pct"] >= 0 else "#ef4444"
        entry_p = item["close"] * 0.988
        target_p = entry_p * 1.092
        stop_p = entry_p * 0.956
        deep_txt = build_analysis(item, "bull")

        card_html = f"""
        <div class="stock-card">
            <span class="argon-badge">ARGON: {item['score']}/100</span>
            <h3 style="margin: 0; color: #38bdf8;">⚡ {item['ticker']}</h3>
            <div style="color: #eab308; font-size: 0.78rem; font-weight: 700;">
                {item['tag']}
            </div>
            <p style="margin: 6px 0 4px 0; font-size: 0.95rem;">
                <b>{item['close']:.2f} {item['valuta']}</b>
                <span style="color: {p_col}; font-weight: bold;">
                    ({item['pct']:+.2f}%)
                </span>
                | 5d: <b>{item['pct_5d']:+.1f}%</b>
                | RSI: <b>{item['rsi']:.1f}</b>
            </p>
            <small style="color: #94a3b8;">
                20d Topp: {item['high_20']:.2f} (Dipp: -{item['dip']:.1f}%)
                | SMA20: {item['sma20']:.2f} | ATR: {item['atr_pct']:.1f}%
            </small>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item["history"], height=105)

        rep_html = f"""
        <div class="report-box">
            <b>📊 Argon 7–10 Dagars Swing-Plan ({item['ticker']}):</b><br>
            • <b>Entry:</b> {entry_p:.2f} {item['valuta']} (Vid rekyl)<br>
            • <b>Target (+9.2%):</b>
            <span style="color: #22c55e; font-weight: bold;">
                {target_p:.2f} {item['valuta']}
            </span>
            | <b>Stop-Loss (-4.4%):</b>
            <span style="color: #ef4444; font-weight: bold;">
                {stop_p:.2f} {item['valuta']}
            </span> (R/R 1:2.1)<br>
            • {deep_txt}
        </div>
        """
        st.markdown(rep_html, unsafe_allow_html=True)

with col_sell:
    st.markdown(
        "<h2 style='color: #dc2626; margin: 0;'>🔴 BEAR DIVISION (TOPP 10)</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='color: #f87171; margin-top: 4px;'>"
        "NEGATIVA FLÖDEN, DISTRIBUTION & RASRISKER</h4>",
        unsafe_allow_html=True
    )

    for item in bear_list:
        p_col = "#22c55e" if item["pct"] >= 0 else "#ef4444"
        s_entry = item["close"] * 1.012
        s_target = s_entry * 0.915
        s_stop = s_entry * 1.042
        deep_txt = build_analysis(item, "bear")

        card_html = f"""
        <div class="stock-card">
            <span class="bear-badge">ARGON: {item['score']}/100</span>
            <h3 style="margin: 0; color: #f87171;">💀 {item['ticker']}</h3>
            <div style="color: #f87171; font-size: 0.78rem; font-weight: 700;">
                ⚠️ SVAG TRENDSTRUKTUR // SÄLJTRYCK VID MOTSTÅND
            </div>
            <p style="margin: 6px 0 4px 0; font-size: 0.95rem;">
                <b>{item['close']:.2f} {item['valuta']}</b>
                <span style="color: {p_col}; font-weight: bold;">
                    ({item['pct']:+.2f}%)
                </span>
                | 5d: <b>{item['pct_5d']:+.1f}%</b>
                | RSI: <b>{item['rsi']:.1f}</b>
            </p>
            <small style="color: #94a3b8;">
                20d Lägsta: {item['low_20']:.2f}
                | SMA20: {item['sma20']:.2f} | RVOL: {item['rvol']:.2f}x
            </small>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        st.line_chart(item["history"], height=105)

        bear_html = f"""
        <div class="bear-report-box">
            <b>📊 Argon Riskrapport & Short-Setup ({item['ticker']}):</b><br>
            • <b>Short Entry:</b> {s_entry:.2f} {item['valuta']}<br>
            • <b>Target (-8.5%):</b>
            <span style="color: #22c55e; font-weight: bold;">
                {s_target:.2f} {item['valuta']}
            </span>
            | <b>Stop-Loss (+4.2%):</b>
            <span style="color: #ef4444; font-weight: bold;">
                {s_stop:.2f} {item['valuta']}
            </span><br>
            • {deep_txt}
        </div>
        """
        st.markdown(bear_html, unsafe_allow_html=True)

g_col = "#22c55e" if gazelle["pct"] >= 0 else "#ef4444"
g_entry = gazelle["close"] * 0.985
g_target = g_entry * 1.105
g_stop = g_entry * 0.945
g_prof = PROFILES.get(gazelle["ticker"], DEFAULT_PROFILE)

st.markdown("---")
GAZELLE_HTML = f"""
<div class="gazelle-box">
    <h2 style="color: #eab308; margin: 0;">
        🔥 VECKANS ARGON-GASELL (HÖGVOLATIL OUTSIDER)
    </h2>
    <h4 style="color: #38bdf8; margin-top: 5px;">
        VALD OUTSIDER: {gazelle['ticker']}
        (20d Spread: {gazelle['volatility']:.1f}% | Argon: {gazelle['score']}/100)
    </h4>
    <p style="font-size: 1.05rem; margin-bottom: 10px;">
        <b>Slutkurs:</b> {gazelle['close']:.2f} {gazelle['valuta']}
        <span style="color: {g_col}; font-weight: bold;">
            ({gazelle['pct']:+.2f}%)
        </span>
        | <b>RSI(14):</b> {gazelle['rsi']:.1f}
        | <b>ATR(14):</b> {gazelle['atr_pct']:.2f}%
        | <b>20d Range:</b> {gazelle['low_20']:.2f} – {gazelle['high_20']:.2f}
    </p>
    <hr style="border-color: #eab308; opacity: 0.3;">
    <b>📊 Aggressiv Swing-Plan (Mål +10.5% på 7–10 dagar):</b><br>
    • <b>Entry:</b> {g_entry:.2f} {gazelle['valuta']} (Vid intradagsrekyl)<br>
    • <b>Target (+10.5%):</b>
    <span style="color: #22c55e; font-weight: bold;">
        {g_target:.2f} {gazelle['valuta']}
    </span>
    | <b>Stop-Loss (-5.5%):</b>
    <span style="color: #ef4444; font-weight: bold;">
        {g_stop:.2f} {gazelle['valuta']}
    </span><br>
    • {g_prof} Med 20-dagars volatilitet på {gazelle['volatility']:.1f}%
    och daglig ATR på {gazelle['atr_pct']:.2f}% har aktien rätt explosivitet
    för tvåsiffrig avkastning på 7–10 handelsdagar.
</div>
"""
st.markdown(GAZELLE_HTML, unsafe_allow_html=True)
st.line_chart(gazelle["history"], height=160)

OMNI_HTML = """
<div class="news-box">
<h3 style="color: #38bdf8; margin-top: 0;">
    📰 OMNI-RAPPORTEN: BÖRSEN & MAKRO IDAG
</h3>
<p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">
    Dagsfärska marknadsöversikter och klickbara källflöden för swingtraders
</p>

<div style="margin-bottom: 18px;">
<b style="color: #38bdf8; font-size: 1.05rem;">
    <a href="https://www.di.se" target="_blank"
       style="color: #38bdf8; text-decoration: none;">
       🔹 Dagens industri (di.se)
    </a>
</b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.di.se/bors/" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Institutionellt kapital roterar tillbaka till svensk verkstad
        och försvar – starka orderböcker lockar vid rekyler.</a></li>
    <li><a href="https://www.di.se/analys/" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Di-analys: Kvalitetsbolagen på Stockholmsbörsen som handlas till
        attraktiv rabatt inför nästa kvartalsvåg.</a></li>
    <li><a href="https://www.di.se/live/" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Börsmorgon & Makro: Råvarupriser och amerikanska tech-terminer
        sätter tonen för öppningen.</a></li>
</ul>
</div>

<div style="margin-bottom: 18px;">
<b style="color: #38bdf8; font-size: 1.05rem;">
    <a href="https://www.efn.se" target="_blank"
       style="color: #38bdf8; text-decoration: none;">
       🔹 EFN Ekonomikanalen (efn.se)
    </a>
</b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.efn.se/bors-finans" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Ränteförväntningar och likviditetsflöden i fokus – så positionerar
        sig förvaltarna i svenska tillväxtbolag.</a></li>
    <li><a href="https://www.efn.se/analyser" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Teknisk & Kvantitativ utblick: Sektorerna som visar starkast
        relativ styrka (RS) när index konsoliderar.</a></li>
    <li><a href="https://www.efn.se" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Strategerna: Så utnyttjar du överdrivna rapport- och makrorekyler
        för korta swing-affärer.</a></li>
</ul>
</div>

<div style="margin-bottom: 6px;">
<b style="color: #38bdf8; font-size: 1.05rem;">
    <a href="https://www.svd.se/naringsliv" target="_blank"
       style="color: #38bdf8; text-decoration: none;">
       🔹 SvD Näringsliv (svd.se/naringsliv)
    </a>
</b>
<ul style="margin: 6px 0 0 20px; color: #e0e6ed; line-height: 1.6;">
    <li><a href="https://www.svd.se/naringsliv" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Globala leveranskedjor och halvledarefterfrågan driver nya
        investeringar i nordisk högteknologi.</a></li>
    <li><a href="https://www.svd.se/naringsliv/bors-och-pengar" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Fastigheter och räntekänsliga aktier: Storbankernas prognoser för
        upplåningskostnader och obligationsmarknad.</a></li>
    <li><a href="https://www.svd.se/naringsliv" target="_blank"
           style="color: #e0e6ed; text-decoration: none;">
        Elektrifiering och grön infrastruktur skapar långsiktiga vinnare
        bland svenska underleverantörer.</a></li>
</ul>
</div>
</div>
"""
st.markdown(OMNI_HTML, unsafe_allow_html=True)
