"""Send the digest through Gmail SMTP."""

import logging
import smtplib
import sys
from email.message import EmailMessage

from . import config

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_TIMEOUT = 30

log = logging.getLogger(__name__)


def send_email(subject, html, text):
    config.require("GMAIL_USER", "GMAIL_APP_PASSWORD", "EMAIL_TO")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = config.GMAIL_USER
    msg["To"] = config.EMAIL_TO
    msg.set_content(text)
    msg.add_alternative(html, subtype="html")

    # Exit non-zero on failure so GitHub Actions marks the run as failed.
    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT) as smtp:
            smtp.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail login failed: check GMAIL_USER and GMAIL_APP_PASSWORD (must be an app password).")
        sys.exit(1)
    except (smtplib.SMTPException, OSError) as e:
        # Exception text comes from the server/socket, never from our credentials.
        log.error("Sending email failed: %s: %s", type(e).__name__, e)
        sys.exit(1)

    log.info("Email sent")
