# ----------------------------------------------------
# Skicka rapporten via e-post
# ----------------------------------------------------
print(f"3. Förbereder utskick från {EMAIL_ADDRESS} till mottagare: {MAIL_RECEIVER}...")

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
print(f"[✓] E-postrapporten har skickats framgångsrikt till {MAIL_RECEIVER}!")
