import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Breddad lista med högvolatila Small/Mid/Large Cap-aktier
tickers = [
    # Sverige (SEK)
    "VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "SSAB-B.ST", "LUND-B.ST",
    "ACAST.ST", "SWECO-B.ST", "STOR-B.ST", "SBB-B.ST", "HACK.ST",
    "FING-B.ST", "SINCH.ST", "EMBRAC-B.ST", "ALLEI.ST",
    # USA (USD)
    "NVDA", "TSLA", "AMD", "PLTR", "AAPL", "SOFI", "MARA", "RIOT", "IONQ", "SMCI"
]

print("1. Skannar utökad aktielista med bredare riskparametrar...")
stock_summaries = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        # Minskat krav på historik för att inte missa nyare/rörliga bolag
        if df.empty or len(df) < 30:
            continue

        latest = df.iloc[-1]
        close_price = latest['Close']
        
        is_swedish = ticker.endswith(".ST")
        valuta = "SEK" if is_swedish else "USD"
        
        # BREDARE PRISFILTER: 10-300 SEK / 2-50 USD
        min_price = 10.0 if is_swedish else 2.0
        max_price = 300.0 if is_swedish else 50.0
        
        # Om aktien ligger utanför intervallet, ta med den ändå om det är en känd USA-jätte
        if not (min_price <= close_price <= max_price) and ticker not in ["NVDA", "TSLA", "AMD"]:
            continue

        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        
        sma_50 = latest['SMA_50'] if pd.notna(latest['SMA_50']) else close_price
        rsi = latest['RSI'] if pd.notna(latest['RSI']) else 50.0
        
        # Mjukare Stop-Loss: 3-dagars lägsta minus 1.5% marginal
        stop_loss = df['Low'].iloc[-3:].min() * 0.985
        risk_amount = close_price - stop_loss
        
        # Skulle stop-loss hamna över eller för nära kursen lägger vi en schablon på 4%
        if risk_amount <= 0:
            stop_loss = close_price * 0.96
            risk_amount = close_price - stop_loss

        target_reward_ratio = 2.5  # Sänkt R/R från 3.0 till 2.5 för att fånga fler setups
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
    raise RuntimeError("Inga aktier kunde beräknas. Kontrollera yfinance-anslutningen.")

market_data_text = "\n".join(stock_summaries)

print(f"2. Skickar {len(stock_summaries)} aktier till AI-agenten...")

prompt = f"""
Du är en aggressiv swingtrader som letar efter hög volatilitet och starka momentum-setups.
Här är färsk kursdata för filtrerade aktier:

{market_data_text}

Välj ut de TOPP 3 absolut mest intressanta kandidaterna för en swingtrade (horisont 3-10 dagar).
Du FÅR ta högre risk om uppsidan och momentumet motiverar det.

Ranka dem (1, 2, 3) och ange tydligt:
1. Bolag & Ticker
2. Entry (Nuvarande pris), Stop-Loss och Målkurs (Take-Profit)
3. Risk/Reward-ratio och beräknad procentuell upp-/nedsida
4. En het och direkt motivering (t.ex. RSI-översålt, bryter ut över SMA50, hög volatilitet).

Skriv rapporten på svenska.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på aggressiv momentum- och swingtrading i volatile aktier."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4
)

ai_report = response.choices[0].message.content

print("\n\n" + "="*60)
print("🤖 HÄR ÄR DIN AI SWING-RAPPORT (HIGH RISK / HIGH REWARD TOPP 3):")
print("="*60)
print(ai_report)
print("="*60 + "\n\n")
