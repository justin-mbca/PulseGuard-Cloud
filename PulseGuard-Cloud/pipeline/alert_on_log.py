
import os
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/pipeline.log')
ALERT_EMAIL = os.environ.get('PG_ALERT_EMAIL')  # Set this in your .env
SMTP_SERVER = os.environ.get('PG_SMTP_SERVER', 'localhost')
SMTP_PORT = int(os.environ.get('PG_SMTP_PORT', 25))
SMTP_USER = os.environ.get('PG_SMTP_USER')
SMTP_PASS = os.environ.get('PG_SMTP_PASS')

# Scan log for WARNING or ERROR
with open(LOG_FILE, 'r') as f:
    log_content = f.read()

matches = re.findall(r'^(.* (WARNING|ERROR) .*)$', log_content, re.MULTILINE)
if matches and ALERT_EMAIL:
    msg = EmailMessage()
    msg['Subject'] = 'Pipeline Alert: Warning/Error Detected'
    msg['From'] = ALERT_EMAIL
    msg['To'] = ALERT_EMAIL
    msg.set_content('\n'.join([m[0] for m in matches]))
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if SMTP_USER and SMTP_PASS:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Alert email sent to {ALERT_EMAIL}.")
    except Exception as e:
        print(f"Failed to send alert email: {e}")
else:
    print("No warnings/errors found or ALERT_EMAIL not set.")
