import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yfinance as yf
import pandas as pd
import ta
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

tickers = [
    "VOLV-B.ST", "ERIC-B.ST", "AZN.ST", "TELIA.ST", "INVE-B.ST",
    "SHB-A.ST", "SEB-A.ST", "ABB.ST", "ASSA-B.ST",
    "AAPL", "MSFT", "GOOGL", "AMZN", "BRK-B", "JNJ", "PG"
]

print("1. Lågriskagenten skannar kvalitetbolag...")
stock_data_list = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if df.empty or len(df) < 30:
            continue

        latest = df.iloc[-1]
        close_price = latest['Close']
        low_10 = df['Low'].iloc[-10:].min()
        
        is_swedish = ticker.endswith(".ST")
        valuta = "SEK" if is_swedish else "USD"
        
        min_price = 30.0 if is_swedish else 10.0
        if close_price < min_price:
            continue

        sma_50_series = ta.trend.sma_indicator(df['Close'], window=50)
        sma_50 = sma_50_series.iloc[-1] if not sma_50_series.empty and pd.notna(sma_50_series.iloc[-1]) else close_price
        
        rsi_series = ta.momentum.rsi(df['Close'], window=14)
        rsi = rsi_series.iloc[-1] if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0
        
        data_summary = (
            f"Ticker: {ticker} | Kurs: {close_price:.2f} {valuta} | "
            f"SMA 50: {sma_50:.2f} | 10d Support: {low_10:.2f} | RSI: {rsi:.1f}"
        )
        stock_data_list.append(data_summary)
    except Exception as e:
        continue

market_text = "\n".join(stock_data_list)

print("2. AI utför analys för stabil portfölj...")
prompt = f"""
Du är en disciplinerad portföljförvaltare med fokus på kapitalbevarande och stabil tillväxt (horisont 20-30 dagar).
Här är marknadsdata för stabila Large Cap-bolag:

{market_text}

STEG 1: Analysera det bredare marknadsläget för de stora börserna.
STEG 2: Välj ut de 5 starkaste kandidaterna som befinner sig i hälsosamma upptrender.
STEG 3: Hårdgranska dessa 5 för att identifiera exakt när en aktie är "i köpläge" via sunda rekyler mot stöd eller glidande medelvärden.

Formatera rapporten professionellt på svenska med:
1. **Makro & Marknadsläge (Large Cap)**
2. **Top 5 Hårdgranskade Kvalitetskandidater** innehållande:
   - **Bolag & Ticker**
   - **Exakt Köpläge (Rekylnivå / Supportzon)**
   - **Entry-nivå**
   - **Stop-Loss & Risk (%)**
   - **Target / Målkurs**
   - **Motivering baserad på trend och fundamental stabilitet**
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är en konservativ och noggrann förvaltare med fokus på riskhantering och träffsäkra rekylköp."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.3
)

ai_report = response.choices[0].message.content

# Skriv ut rapporten direkt i GitHub-loggen
print("\n" + "="*50 + "\nLÅGRISK-RAPPORT:\n" + "="*50 + "\n")
print(ai_report)
print("\n" + "="*50 + "\n")

print("3. Skickar e-postrapport (Lågrisk)...")
if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = "🛡️ Lågrisk-Agent: Kvalitetsanalys & Rekylnivåer"
    msg.attach(MIMEText(ai_report, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Lågrisk-rapport skickad via e-post!")
    except Exception as e:
        print(f"E-postfel: {e}")
