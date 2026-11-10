import os
import yfinance as yf
import pandas as pd
import numpy as np
import ta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==================== ARGON v2.0 AUTOMATION AGENT ====================

TICKERS = [
    "VOLV-B.ST", "SAAB-B.ST", "MYCR.ST", "BONE.ST", "CAMX.ST",
    "ATCO-A.ST", "ABB.ST", "SAND.ST", "HEXA-B.ST", "EVOL.ST",
    "BOL.ST", "SSAB-B.ST", "FNOX.ST", "NIBE-B.ST", "EMBRAC-B.ST",
    "SINCH.ST", "SBB-B.ST", "ERIC-B.ST", "HM-B.ST", "GETI-B.ST",
    "INVE-B.ST", "SEB-A.ST", "TELIA.ST", "NVDA", "AMD",
    "PLTR", "TSLA", "SMCI", "CRWD", "ARM", "AAPL", "MSFT"
]

def run_agent_scanner():
    print("Startar Argon v2.0 marknadsscanning...")
    
    # Hämta index för RS-Alpha
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
    for ticker in TICKERS:
        try:
            df = yf.Ticker(ticker).history(period="3mo")
            if df.empty or len(df) < 20:
                continue
            close, high, low, vol = df["Close"], df["High"], df["Low"], df["Volume"]
            c_now, c_prev = float(close.iloc[-1]), float(close.iloc[-2])
            pct_1d = ((c_now - c_prev) / c_prev) * 100
            c_5d = float(close.iloc[-6]) if len(close) >= 6 else c_prev
            pct_5d = ((c_now - c_5d) / c_5d) * 100

            is_se = ticker.endswith(".ST")
            valuta = "SEK" if is_se else "USD"
            rs_alpha = pct_5d - (omx_5d if is_se else spx_5d)

            rsi_s = ta.momentum.rsi(close=close, window=14)
            rsi_v = float(rsi_s.iloc[-1]) if not pd.isna(rsi_s.iloc[-1]) else 50.0
            sma20 = float(close.tail(20).mean())
            sma50 = float(close.tail(50).mean()) if len(close) >= 50 else sma20
            high_20 = float(high.tail(20).max())

            tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
            atr_14 = float(tr.tail(14).mean())
            
            avg_vol = float(vol.tail(20).mean())
            rvol = (float(vol.iloc[-1]) / avg_vol) if avg_vol > 0 else 1.0
            dip_high = ((high_20 - c_now) / high_20) * 100

            score = 50.0
            if c_now > sma50: score += 12.0
            if sma20 >= sma50: score += 8.0
            if rs_alpha > 0.5: score += 10.0
            if 2.0 <= dip_high <= 12.0 and c_now >= sma50 * 0.95: score += 14.0
            if 35.0 <= rsi_v <= 56.0: score += 12.0
            if atr_14 > 0: score += 6.0
            
            argon_score = int(np.clip(score, 10, 99))

            results.append({
                "ticker": ticker,
                "close": c_now,
                "valuta": valuta,
                "pct": pct_1d,
                "rs_alpha": rs_alpha,
                "rsi": rsi_v,
                "atr": atr_14,
                "score": argon_score
            })
        except Exception:
            continue

    # Sortera fram topp 5 guldkorn
    sorted_bull = sorted(results, key=lambda x: (x["score"], x["rs_alpha"]), reverse=True)[:5]
    
    report_lines = ["👑 DAGENS SWINGKINGS ARGON-RAPPORT\n", "Här är dagens topp 5 kvantitativa guldkorn för swingtrade (7-10 dagar):\n"]
    for i, stock in enumerate(sorted_bull, 1):
        entry = stock["close"] - (0.35 * stock["atr"])
        target = entry + (3.2 * stock["atr"])
        stop = entry - (1.6 * stock["atr"])
        line = (
            f"{i}. {stock['ticker']} ({stock['close']:.2f} {stock['valuta']} | {stock['pct']:+.2f}%)\n"
            f"   • Argon Score: {stock['score']}/100 | RS-Alpha: {stock['rs_alpha']:+.1f}%\n"
            f"   • Rekommenderad Entry: {entry:.2f} {stock['valuta']}\n"
            f"   • Target: {target:.2f} {stock['valuta']} | Stop-Loss: {stop:.2f} {stock['valuta']}\n"
        )
        report_lines.append(line)
        
    report_text = "\n".join(report_lines)
    print(report_text)
    return report_text

def send_email_report(body_content):
    sender_email = os.environ.get("GMAIL_USER", "micke.lejonryde@gmail.com")
    receiver_email = "micke.lejonryde@gmail.com"
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "") # Eller använd SMTP secrets
    
    msg = MIMEMultipart()
    msg["Subject"] = "SWINGKINGS - Dagsaktuell Topp 5 Guldkorn"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.attach(MIMEText(body_content, "plain"))

    try:
        # Om du kör via SMTP eller GitHub Secrets
        print("Skickar e-postrapport...")
        # (Verifiera anslutning mot din e-postleverantör vid behov)
    except Exception as e:
        print(f"Kunde inte skicka e-post: {e}")

if __name__ == "__main__":
    report = run_agent_scanner()
    send_email_report(report)
