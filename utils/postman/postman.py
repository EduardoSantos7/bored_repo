import os
import logging
import smtplib

from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()  # take environment variables from .env.


def send_email(content):
    try:
        sender = os.getenv("NO_REPLAY_EMAIL")
        sender_password = os.getenv("NO_REPLAY_PASS")
        receiver = os.getenv("TARGET_EMAIL")

        msg = MIMEText(content, "html")
        msg["Subject"] = "Test"
        msg["From"] = sender
        msg["To"] = receiver

        s = smtplib.SMTP_SSL(host="smtp.gmail.com", port=465)
        s.login(user=sender, password=sender_password)
        s.sendmail(sender, receiver, msg.as_string())
        s.quit()
    except Exception as e:
        logging.error(e)
