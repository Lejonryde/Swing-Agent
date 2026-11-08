import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

# Hämtar nycklar
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

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

if not stock_summaries:
    raise RuntimeError("Inga aktier kunde hittas.")

market_data_text = "\n".join(stock_summaries)

print("2. Skickar data till AI-agenten för analys...")

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
# SKRIVER UT RAPPORTEN STORT I GITHUB-LOGGEN
# ----------------------------------------------------
print("\n\n" + "="*60)
print("🤖 HÄR ÄR DIN AI SWING-RAPPORT:")
print("="*60)
print(ai_report)
print("="*60 + "\n\n")

# Sparar även ner rapporten som en textfil lokalt i bygget
with open("ai_rapport.txt", "w", encoding="utf-8") as f:
    f.write(ai_report)

print("[✓] Rapport genererad och sparad!")
