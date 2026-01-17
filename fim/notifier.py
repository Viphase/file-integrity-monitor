import logging
import requests
import smtplib
from email.message import EmailMessage

log = logging.getLogger(__name__)

class Notifier:
    def __init__(self, cfg):
        self.tg = cfg.get("telegram", {})
        self.email = cfg.get("email", {})

    def notify(self, title, body):
        
        if self.tg.get("enabled"):
            try:
                self.send_telegram(title, body)
            except Exception:
                log.exception("telegram failed")
        
        if self.email.get("enabled"):
            try:
                self.send_email(title, body)
            except Exception:
                log.exception("email failed")

    def send_telegram(self, title, body):
        token = self.tg.get("bot_token")
        chat_id = self.tg.get("chat_id")
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        text = f"*{title}*\n```\n{body}\n```"
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10).raise_for_status()

    def send_email(self, title, body):
        cfg = self.email

        msg = EmailMessage()
        msg["From"] = cfg.get("sender")
        msg["To"] = cfg.get("receiver")
        msg["Subject"] = title
        msg.set_content(body)
        
        server = smtplib.SMTP(cfg.get("smtp_server"), cfg.get("smtp_port", 25), timeout=10)
        try:
            if cfg.get("use_starttls"):
                server.starttls()
            if cfg.get("username"):
                server.login(cfg.get("username"), cfg.get("password"))
            server.send_message(msg)
        finally:
            server.quit()
