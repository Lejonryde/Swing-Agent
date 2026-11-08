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
    "VOLV-B.ST", "ERIC-B.ST", "SSAB-B.ST", "SBB-B.ST", "TELIA.ST",
    "SINCH.ST", "NVDA", "TSLA", "AMD", "PLTR", "SOFI", "MARA", "RIOT"
]

print("1. Högriskagenten skannar marknaden...")
stock_data_list = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        if df.empty or len(df) < 20:
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

        rsi_series = ta.momentum.rsi(df['Close'], window=14)
        rsi = rsi_series.iloc[-1] if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0
        
        data_summary = (
            f"Ticker: {ticker} | Kurs: {close_price:.2f} {valuta} | "
            f"20d Högsta: {high_20:.2f} | 5d Lägsta (Stöd): {low_5:.2f} | RSI: {rsi:.1f}"
        )
        stock_data_list.append(data_summary)
    except Exception as e:
        continue

market_text = "\n".join(stock_data_list)

print("2. AI utför djupgående marknads- och omvärldsanalys...")
prompt = f"""
Du är en erfaren och aggressiv swingtrader. Din horisont är 7-10 dagar med sikte på 10-15%+ avkastning.
Här är rådata från marknadsskanningen:

{market_text}

STEG 1: Utvärdera marknaden, nuvarande omvärldsflöden och sentiment.
STEG 2: Välj ut de 5 starkaste kandidaterna som har bäst potential för en snabb rörelse på 7-10 dagar.
STEG 3: Hårdgranska dessa 5 kandidater. Definiera glasklart när en aktie är "i köpläge" (t.ex. inte bara blint brott över högsta, utan specifik priszon för återtest, volymkrav eller intradagstryck).

Formatera rapporten professionellt på svenska med:
1. **Marknadsläge & Omvärldsanalys** (Kort lägesrapport)
2. **Top 5 Hårdgranskade Kandidater** där varje aktie innehåller:
   - **Bolag & Ticker**
   - **Exakt Köpläge (När är den i köpläge?):**
   - **Entry-nivå**
   - **Stop-Loss & Risk (%)**
   - **Target / Målkurs (+10-15%)**
   - **Motivering baserad på momentum och kortsiktig potential**
"""

client = OpenAI(api_key=OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Du är en elit-trader som specialiserat sig på kortsiktig swingtrading och riskhantering."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4
)

ai_report = response.choices[0].message.content

# Skriv ut rapporten direkt i GitHub-loggen
print("\n" + "="*50 + "\nHÖGRISK-RAPPORT:\n" + "="*50 + "\n")
print(ai_report)
print("\n" + "="*50 + "\n")

print("3. Skickar e-postrapport (Högrisk)...")
if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECEIVER:
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = "🤖 Högrisk-Agent: Marknadsanalys & Top 5 Triggers"
    msg.attach(MIMEText(ai_report, 'plain', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Högrisk-rapport skickad via e-post!")
    except Exception as e:
        print(f"E-postfel: {e}")
