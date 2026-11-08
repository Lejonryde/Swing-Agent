import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Högvolatil lista: Både småbolag, tillväxt och momentumgiganter
tickers = [
    # Sverige (SEK) - Högre risk / Lägre prisspann
    "VOLV-B.ST", "ERIC-B.ST", "SSAB-B.ST", "SBB-B.ST", "TELIA.ST",
    "SINCH.ST", "SVENT.ST", "CALL.ST", "VICO.ST", "ORX.ST",
    # USA (USD) - Hög momentum & volatilitet
    "NVDA", "TSLA", "AMD", "PLTR", "SOFI", "MARA", "RIOT", "IONQ", "SOUND"
]

print("1. Skannar aktiemarknaden med hög riskprofil...")
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
        
        # LÅGT PRISGOLV FÖR ÖKAD RISK: Från 2 SEK / 0.50 USD
        min_price = 2.0 if is_swedish else 0.50
        max_price = 1000.0 if is_swedish else 500.0
        
        if not (min_price <= close_price <= max_price):
            continue

        sma_50_series = ta.trend.sma_indicator(df['Close'], window=min(50, len(df)))
        rsi_series = ta.momentum.rsi(df['Close'], window=min(14, len(df)))
        
        sma_50 = sma_50_series.iloc[-1] if not sma_50_series.empty and pd.notna(sma_50_series.iloc[-1]) else close_price
        rsi = rsi_series.iloc[-1] if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0
        
        # Stop-Loss sätts snävare/aggressivare för hög Risk/Reward
        stop_loss = low_5 * 0.97 if low_5 < close_price else close_price * 0.94
        risk_amount = close_price - stop_loss
        
        if risk_amount <= 0:
            stop_loss = close_price * 0.94
            risk_amount = close_price - stop_loss

        target_reward_ratio = 3.0  # Höjt till 1:3 R/R för mer aggressiva setups
        take_profit = close_price + (risk_amount * target_reward_ratio)
        
        loss_pct = ((close_price - stop_loss) / close_price) * 100
        gain_pct = ((take_profit - close_price) / close_price) * 100
        
        summary = (
            f"- Bolag: {ticker} | Nuvarande kurs: {close_price:.2f} {valuta} | "
            f"20-dagars Högsta (Motstånd): {high_20:.2f} {valuta} | "
            f"Senaste Lägsta (Support): {low_5:.2f} {valuta} | "
            f"Förslag Stop-Loss: {stop_loss:.2f} {valuta} (-{loss_pct:.1f}%) | "
            f"Förslag Målkurs: {take_profit:.2f} {valuta} (+{gain_pct:.1f}%) | "
            f"RSI: {rsi:.1f} | SMA 50: {sma_50:.2f}"
        )
        stock_summaries.append(summary)
    except Exception as e:
        continue

if not stock_summaries:
    print("Inga aktier kunde behandlas.")
    exit(0)

market_data_text = "\n".join(stock_summaries)

print(f"2. Skickar {len(stock_summaries)} aktier till AI-agenten...")

prompt = f"""
Du är en aggressiv momentum- och breakout-trader. Du söker aktier med hög volatilitet och stor uppsida.
Här är färsk kursdata för filtrerade aktier:

{market_data_text}

Välj ut de TOPP 3 absolut bästa swingtrade-kandidaterna (horisont 2-10 dagar).

VIKTIGT: Du ska ge en KROK/TRIGGER för entry på formatet:
"När [Aktie] når/bryter över X [Valuta], så är det läge att gå in."

Formatera rapporten så här för varje topp 3-kandidat:

### [Rang]. [Bolag/Ticker]
- **Exakt Trigger/Köpsignal:** "När X når Y kr..." (Ange tydlig villkorsstyrd entry, t.ex. utbrott över motstånd eller pullback till support).
- **Nuvarande Kurs:** X
- **Stop-Loss:** X (-Y%)
- **Målkurs (Take-Profit):** X (+Y%)
- **Risk/Reward:** 1:X
- **Teknisk Motivering:** Varför är denna setup het och vad bekräftar utbrottet?

Skriv rapporten på svenska med en vass och direkt ton.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är en aggressiv swingtrader specialiserad på breakout-setups och exakta köpsignaler."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.5
)

ai_report = response.choices[0].message.content

print("\n\n" + "="*60)
print("🤖 HÄR ÄR DIN AI SWING-RAPPORT (HIGH RISK & EXAKTA TRIGGERS):")
print("="*60)
print(ai_report)
print("="*60 + "\n\n")
