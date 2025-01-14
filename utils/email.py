import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import socket

load_dotenv(override=True)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", EMAIL_USERNAME)

def send_email(subject, body):

    message = MIMEMultipart()
    message["From"] = EMAIL_USERNAME
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=5) as server:
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, RECIPIENT_EMAIL, message.as_string())
            return True
    except smtplib.SMTPException as e:
        print(f"SMTP error occured: {e}")
    except socket.timeout as e:
        print(f"Connection timout {e}")
    except Exception as e:
        print(f"Error sending email: {e}")
    return False
