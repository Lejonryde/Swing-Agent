import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Utökat utbud: Blandning av svensk Large/Mid/Small Cap och USA
tickers = [
    # Sverige (SEK)
    "VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "SSAB-B.ST", "LUND-B.ST",
    "ACAST.ST", "SWECO-B.ST", "STOR-B.ST", "SBB-B.ST", "HACK.ST",
    # USA (USD)
    "NVDA", "TSLA", "AMD", "PLTR", "AAPL", "SOFI", "MARA", "RIOT"
]

print("1. Skannar aktier och applicerar pris- & momentumfilter...")
stock_summaries = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty or len(df) < 50:
            continue

        latest = df.iloc[-1]
        close_price = latest['Close']
        
        is_swedish = ticker.endswith(".ST")
        valuta = "SEK" if is_swedish else "USD"
        
        # PRISFILTER: 50-200 SEK för svenska aktier, 5-20 USD för amerikanska
        min_price = 50.0 if is_swedish else 5.0
        max_price = 200.0 if is_swedish else 20.0
        
        if not (min_price <= close_price <= max_price):
            continue

        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
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
    print("Inga aktier matchade prisfiltret (50-200 kr / 5-20 USD).")
    exit()

market_data_text = "\n".join(stock_summaries)

print(f"2. Skickar {len(stock_summaries)} godkända aktier till AI-agenten...")

prompt = f"""
Du är en aggressiv men disciplinerad swingtrader som söker hög momentum.
Här är kursdata för aktier som passerat våra pris- och indikatorfilter:

{market_data_text}

Välj ut de TOPP 3 bästa kandidaterna för en swingtrade (horisont 5-10 dagar).
Ranka dem (1, 2, 3) och ange för varje aktie:
- Exakt Entry, Stop-Loss och Take-Profit (Målkurs)
- Risk/Reward-förhållande
- En kort teknisk motivering till varför uppsättningen är het just nu.

Skriv rapporten på svenska och strukturera den tydligt.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på momentum- och swingtrading i små och medelstora bolag."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

ai_report = response.choices[0].message.content

print("\n\n" + "="*60)
print("🤖 HÄR ÄR DIN AI SWING-RAPPORT (TOPP 3):")
print("="*60)
print(ai_report)
print("="*60 + "\n\n")
