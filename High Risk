import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Hämtar hemligheter från GitHub Secrets
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

# Högvolatil lista
tickers = [
    "VOLV-B.ST", "ERIC-B.ST", "SSAB-B.ST", "SBB-B.ST", "TELIA.ST",
    "SINCH.ST", "NVDA", "TSLA", "AMD", "PLTR", "SOFI", "MARA", "RIOT"
]

print("1. Skannar aktiemarknaden...")
stock_summaries = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if df.empty or len(df) < 10:
            continue

        latest = df.iloc[-1]
        close_price = latest['Close']
        high_20 = df['High'].iloc[-20:].max()
        low_5 = df['Low'].iloc[-5:].min()
        
        is_swedish = ticker.endswith(".ST")
        valuta = "SEK" if is_swedish else "USD"
        
        min_price = 2.0 if is_swedish else 0.50
        max_price = 1000.0 if is_swedish else 500.0
        
        if not (min_price <= close_price <= max_price):
            continue

        sma_50_series = ta.trend.sma_indicator(df['Close'], window=min(50, len(df)))
        rsi_series = ta.momentum.rsi(df['Close'], window=min(14, len(df)))
        
        sma_50 = sma_50_series.iloc[-1] if not sma_50_series.empty and pd.notna(sma_50_series.iloc[-1]) else close_price
        rsi = rsi_series.iloc[-1] if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0
        
        stop_loss = low_5 * 0.97 if low_5 < close_price else close_price * 0.94
        risk_amount = close_price - stop_loss
        
        if risk_amount <= 0:
            stop_loss = close_price * 0.94
            risk_amount = close_price - stop_loss

        target_reward_ratio = 3.0
        take_profit = close_price + (risk_amount * target_reward_ratio)
        
        loss_pct = ((close_price - stop_loss) / close_price) * 100
        gain_pct = ((take_profit - close_price) / close_price) * 100
        
        summary = (
            f"- Bolag: {ticker} | Kurs: {close_price:.2f} {valuta} | "
            f"Motstånd: {high_20:.2f} | Support: {low_5:.2f} | "
            f"SL: {stop_loss:.2f} (-{loss_pct:.1f}%) | TP: {take_profit:.2f} (+{gain_pct:.1f}%) | RSI: {rsi:.1f}"
        )
        stock_summaries.append(summary)
    except Exception as e:
        continue

market_data_text = "\n".join(stock_summaries)

print("2. Genererar AI-rapport...")
prompt = f"""
Du är en aggressiv momentum-trader. Analysera följande data och vaskas fram de TOPP 3 bästa swing-cachen med tydliga entry-triggrar:
{market_data_text}
Skriv rapporten på svenska med en vass och direkt ton.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på momentum- och swingtrading."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.5
)

ai_report = response.choices[0].message.content

print("3. Skickar e-postrapport...")

# Skicka e-post via SMTP (Gmail)
if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = "🤖 AI Swingtrading Rapport - Högrisk"
    
    msg.attach(MIMEText(ai_report, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("E-post skickad framgångsrikt!")
    except Exception as e:
        print(f"Kunde inte skicka e-post: {e}")
else:
    print("E-post-secrets saknas i GitHub, hoppar över utskick.")
