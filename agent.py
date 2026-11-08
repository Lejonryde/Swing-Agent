from xhtml2pdf import pisa

# 1. Bygg HTML-koden för rapporten (med AI-svaret och datan)
html_content = f"""
<html>
<body>
    <h1>AI Swing Trading Rapport</h1>
    <pre>{ai_report}</pre>
</body>
</html>
"""

# 2. Spara som PDF-fil
with open("swing_rapport.pdf", "wb") as pdf_file:
    pisa.CreatePDF(html_content, dest=pdf_file)

print("[✓] PDF-rapport skapad: swing_rapport.pdf")
