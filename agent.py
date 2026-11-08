import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# 100% fungerande tickers på Yahoo Finance
tickers = [
    # Sverige (SEK)
    "VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "SSAB-B.ST", "SBB-B.ST", "TELIA.ST",
    # USA (USD)
    "NVDA", "TSLA", "AMD", "PLTR", "AAPL", "SOFI", "MARA", "RIOT"
]

print("1. Skannar aktielistan...")
stock_summaries = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty or len(df) < 30:
            continue

        latest = df.iloc[-1]
        close_price = latest['Close']
        
        is_swedish = ticker.endswith(".ST")
        valuta = "SEK" if is_swedish else "USD"
        
        # Breda filter så att vi garanterat får träffar
        min_price = 5.0 if is_swedish else 2.0
        max_price = 1000.0 if is_swedish else 200.0
        
        if not (min_price <= close_price <= max_price):
            continue

        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        sma_50 = latest['SMA_50'] if pd.notna(latest['SMA_50']) else close_price
        rsi = latest['RSI'] if pd.notna(latest['RSI']) else 50.0
        
        stop_loss = df['Low'].iloc[-3:].min() * 0.985
        risk_amount = close_price - stop_loss
        
        if risk_amount <= 0:
            stop_loss = close_price * 0.95
            risk_amount = close_price - stop_loss

        target_reward_ratio = 2.5
        take_profit = close_price + (risk_amount * target_reward_ratio)
        
        loss_pct = ((close_price - stop_loss) / close_price) * 100
        gain_pct = ((take_profit - close_price) / close_price) * 100
        
        summary = (
            f"- Bolag: {ticker} | Pris: {close_price:.2f} {valuta} | "
            f"Stop-Loss: {stop_loss:.2f} {valuta} (-{loss_pct:.1f}%) | "
            f"Målkurs: {take_profit:.2f} {valuta} (+{gain_pct:.1f}%) | "
            f"RSI: {rsi:.1f} | SMA 50: {sma_50:.2f}"
        )
        stock_summaries.append(summary)
    except Exception as e:
        continue

if not stock_summaries:
    raise RuntimeError("Inga aktier matchade filtren.")

market_data_text = "\n".join(stock_summaries)

print(f"2. Skickar {len(stock_summaries)} aktier till AI-agenten...")

prompt = f"""
Du är en aggressiv swingtrader som söker starka momentum-setups.
Här är aktuell kursdata för godkända aktier:

{market_data_text}

Välj ut de TOPP 3 absolut bästa kandidaterna för en swingtrade (horisont 3-10 dagar).
Ranka dem (1, 2, 3) och ange för varje aktie:
- Bolag & Ticker
- Exakt Entry, Stop-Loss och Take-Profit (Målkurs)
- Risk/Reward-förhållande och procentuell upp-/nedsida
- En kort och vass motivering baserat på RSI och trend.

Skriv rapporten på svenska.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på momentum- och swingtrading."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4
)

ai_report = response.choices[0].message.content

print("\n\n" + "="*60)
print("🤖 HÄR ÄR DIN AI SWING-RAPPORT (TOPP 3):")
print("="*60)
print(ai_report)
print("="*60 + "\n\n")
