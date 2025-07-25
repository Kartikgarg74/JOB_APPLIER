import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", os.getenv("SMTP_USER"))

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def send_email(to_email: str, subject: str, body: str, html: str = None):
    """
    Sends an email using SendGrid if configured, otherwise falls back to SMTP.
    :param to_email: Recipient email address
    :param subject: Email subject
    :param body: Plain text body
    :param html: Optional HTML body
    """
    if SENDGRID_API_KEY and SENDGRID_AVAILABLE:
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body,
            html_content=html or body,
        )
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            print(f"SendGrid error: {e}. Falling back to SMTP.")
            # Fallback to SMTP
            _send_email_smtp(to_email, subject, body, html)
    else:
        _send_email_smtp(to_email, subject, body, html)


def _send_email_smtp(to_email: str, subject: str, body: str, html: str = None):
    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    part1 = MIMEText(body, "plain")
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, "html")
        msg.attach(part2)
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

# --- SMS Service Integration (Twilio) ---
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

def send_sms(to_number: str, message: str):
    """
    Sends an SMS using Twilio if configured, otherwise prints for demo.
    :param to_number: Recipient phone number (E.164 format, e.g., +1234567890)
    :param message: SMS message body
    """
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER and TWILIO_AVAILABLE:
        try:
            client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=TWILIO_FROM_NUMBER,
                to=to_number
            )
        except Exception as e:
            print(f"Twilio error: {e}. SMS not sent.")
    else:
        print(f"[SMS DEMO] To: {to_number} | Message: {message}")
