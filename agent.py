import os
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI
import discord
import asyncio

# Hämtar nycklarna säkert från GitHub Secrets
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID"))

tickers = [
    "ACAST.ST", "CAMX.ST", "CRADB.ST", "ADDT.ST", "AFRY.ST"
]

print("1. Skannar tillväxtbolag och beräknar indikatorer...")
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
        
        summary = (
            f"- Bolag: {ticker} | Pris: {close_price:.2f} SEK | "
            f"Stop-Loss: {stop_loss:.2f} SEK (-{loss_pct:.1f}%) | "
            f"Målkurs: {take_profit:.2f} SEK (+{gain_pct:.1f}%) | "
            f"RSI: {rsi:.2f} | SMA 50: {sma_50:.2f}"
        )
        stock_summaries.append(summary)
    except Exception as e:
        continue

market_data_text = "\n".join(stock_summaries)

print("2. Skickar data till AI-agenten för analys...\n")

prompt = f"""
Du är en aggressiv men disciplinerad tillväxt-trader specialiserad på swingtrading. 
Investeraren siktar på 7-10% avkastning per affär (horisont 7-10 dagar). 

Här är dagsdata för tillväxtbolag:
{market_data_text}

Välj ut den 1 absolut hetaste kandidaten, föreslå exakt Entry, Stop-Loss och Take-Profit, samt en kort riskvarning. Håll det koncist och lättläst för Discord.
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är expert på momentumtrading."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

ai_report = response.choices[0].message.content

# Skicka till Discord
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Boten är inloggad som {bot.user}")
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel:
        message = f"🤖 **AI SWING-RAPPORT** 🤖\n\n{ai_report}"
        await channel.send(message)
        print("[✓] Rapporten har skickats till din Discord-kanal!")
    else:
        print("[X] Hittade inte kanalen.")
    await bot.close()

async def main():
    async with bot:
        await bot.start(DISCORD_BOT_TOKEN)

asyncio.run(main())
