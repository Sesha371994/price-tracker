"""
Email alert module — sends a notification when a tracked product's
price drops to or below its target price.

Uses Gmail SMTP by default. To use it:
1. Enable 2FA on your Gmail account
2. Generate an "App Password": Google Account -> Security -> App passwords
3. Set these as environment variables (don't hardcode credentials):
   EMAIL_SENDER=youraddress@gmail.com
   EMAIL_APP_PASSWORD=your-16-char-app-password
   EMAIL_RECEIVER=whereyouwantalerts@gmail.com
"""
import os
import smtplib
from email.mime.text import MIMEText

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def is_email_configured() -> bool:
    return bool(
        os.environ.get("EMAIL_SENDER")
        and os.environ.get("EMAIL_APP_PASSWORD")
        and os.environ.get("EMAIL_RECEIVER")
    )


def send_price_alert(product_name: str, price: float, target: float, url: str):
    """Send an email when a product hits its target price. Returns (success, message)."""
    sender = os.environ.get("EMAIL_SENDER")
    app_password = os.environ.get("EMAIL_APP_PASSWORD")
    receiver = os.environ.get("EMAIL_RECEIVER")

    if not (sender and app_password and receiver):
        return False, "Email not configured (set EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECEIVER env vars)"

    subject = f"🎯 Price Alert: {product_name} hit ₹{price:,.2f}"
    body = (
        f"Good news!\n\n"
        f"{product_name}\n"
        f"Current price: ₹{price:,.2f}\n"
        f"Your target: ₹{target:,.2f}\n\n"
        f"Buy it here: {url}\n"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(sender, app_password)
            server.sendmail(sender, receiver, msg.as_string())
        return True, "Alert email sent"
    except Exception as e:
        return False, f"Failed to send email: {e}"
