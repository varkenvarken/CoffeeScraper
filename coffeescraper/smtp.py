# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

from .utils import get_secret, get_env

def send_message(sender: str, recipient: str, subject: str, message: str) -> None:

    if get_env("DRYRUN") is not None:
        logging.info(f"mail to {recipient} skipped\nMessage was:\n{message}")
        return
    
    username = get_secret("/run/secrets/smtp_user")
    password = get_secret("/run/secrets/smtp_password")
    smtphost = get_secret("/run/secrets/smtp_host")

    # Create a MIMEText object for the message
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = ",".join(recipient) if type(recipient) == list else recipient
    msg["Subject"] = Header(subject, "utf-8")


    # Attach the message body
    msg.attach(MIMEText(message, "plain"))

    with smtplib.SMTP_SSL(smtphost, 465) as server:
        server.login(username, password)
        server.sendmail(sender, recipient, msg.as_string())
        logging.info(f"message with subject {subject} sent to {recipient}")
