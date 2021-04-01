import os
import smtplib

from email.mime.text import MIMEText


def send_email(content):
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
