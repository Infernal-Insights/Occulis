import os
import smtplib
import httpx
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(os.path.join('config', 'secrets.env'))

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
EMAIL_TO = os.getenv('EMAIL_TO')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')


class Notifier:
    def __init__(self):
        self.smtp_server = SMTP_SERVER

    def send_email(self, message: str):
        if not self.smtp_server:
            return
        msg = MIMEText(message)
        msg['Subject'] = 'Occulis Alert'
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO
        with smtplib.SMTP(self.smtp_server) as s:
            if SMTP_USER and SMTP_PASS:
                s.login(SMTP_USER, SMTP_PASS)
            s.sendmail(SMTP_USER, [EMAIL_TO], msg.as_string())

    async def send_webhook(self, payload: dict):
        if not WEBHOOK_URL:
            return
        async with httpx.AsyncClient() as client:
            await client.post(WEBHOOK_URL, json=payload)
