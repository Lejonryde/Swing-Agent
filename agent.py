import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Hämtar nycklar och e-postinställningar
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
MAIL_RECEIVER = os.environ.get("MAIL_RECEIVER")

tickers = [
    "VOLV-B.ST", "ERIC-B.ST", "AZN.ST",
    "NVDA", "TSLA", "AMD", "PLTR", "AAPL"
]

print("1. Skannar aktier (Sverige & USA) och beräknar indikatorer...")
stock_summaries = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty or len(df) < 50:
            continue

        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        latest = df.iloc[-1]
        close_price = latest['Close']
        sma_50 = latest['SMA_50']
        rsi = latest['RSI']
        
        stop_loss = df['Low'].iloc[-5:].min() * 0.98
        risk_amount = close_price - stop_loss
        if risk_amount <= 0:
            continue
            
        target_reward_ratio = 3.0
        take_profit = close_price + (risk_amount * target_reward_ratio)
        
        loss_pct = ((close_price - stop_loss) / close_price) * 100
        gain_pct = ((take_profit - close_price) / close_price) * 100
        
        valuta = "USD" if not ticker.endswith(".ST") else "SEK"
        
        summary = (
            f"- Bolag: {ticker} | Pris: {close_price:.2f} {valuta} | "
            f"Stop-Loss: {stop_loss:.2f} {valuta} (-{loss_pct:.1f}%) | "
            f"Målkurs: {take_profit:.2f} {valuta} (+{gain_pct:.1f}%) | "
            f"RSI: {rsi:.2f} | SMA 50: {sma_50:.2f}"
        )
        stock_summaries.append(summary)
    except Exception as e:
        continue

market_data_text = "\n".join(stock_summaries)

print("\n2. Skickar data till AI-agenten för analys...")

prompt = f"""
Du är en aggressiv men disciplinerad swingtrader.
Här är aktuell kursdata för utvalda svenska och amerikanska aktier:

{market_data_text}

Välj ut den 1 absolut hetaste kandidaten för en swingtrade (horisont 5-10 dagar).
Ange exakt Entry, Stop-Loss, Take-Profit och en kort motivering. Skriv rapporten på svenska.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på momentum- och swingtrading."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

ai_report = response.choices[0].message.content

# ----------------------------------------------------
# Skriv ut AI-rapporten i loggen FÖRE e-postutskicket
# ----------------------------------------------------
print("\n" + "="*50)
print("🤖 AI SWING-RAPPORT")
print("="*50)
print(ai_report)
print("="*50 + "\n")

# Try-except runt e-postutskicket så att rapporten alltid skrivs ut oavsett om mejlet kraschar
try:
    print(f"3. Förbereder e-postutskick till {MAIL_RECEIVER}...")
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = MAIL_RECEIVER
    msg['Subject'] = "🤖 Din automatiska AI Swing-rapport"
    msg.attach(MIMEText(ai_report, 'plain', 'utf-8'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, MAIL_RECEIVER, msg.as_string())
    server.quit()
    print("[✓] E-postrapporten har skickats framgångsrikt!")
except Exception as e:
    print(f"[X] E-postutskick misslyckades: {e}")
