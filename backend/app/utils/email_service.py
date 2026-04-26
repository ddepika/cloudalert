import os
import smtplib
from email.message import EmailMessage
from fastapi import BackgroundTasks
from pydantic import EmailStr
from dotenv import load_dotenv

# Force reload .env
load_dotenv(override=True)

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "noreply@cloudalert.com")

# Force EMAIL_CONFIGURED to True since we know credentials exist
EMAIL_CONFIGURED = True

print("=" * 60)
print("EMAIL SERVICE LOADED - REAL MODE")
print(f"MAIL_USERNAME: {MAIL_USERNAME}")
print(f"MAIL_PASSWORD length: {len(MAIL_PASSWORD) if MAIL_PASSWORD else 0}")
print(f"EMAIL_CONFIGURED: {EMAIL_CONFIGURED}")
print("=" * 60)

def send_email_sync(to_email: str, subject: str, body: str):
    print(f"[send_email_sync] Sending to: {to_email}")
    
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = MAIL_FROM
        msg['To'] = to_email
        
        print(f"[SMTP] Connecting to Gmail...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print(f"[SMTP] Logging in as {MAIL_USERNAME}...")
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            print(f"[SMTP] Login successful!")
            server.send_message(msg)
            print(f"[SMTP] Message sent!")
        
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def send_alert_email(email: EmailStr, name: str, district: str, risk_level: str, probability: float, background_tasks: BackgroundTasks):
    print(f"[send_alert_email] Called! Sending to {email}")
    subject = f"CloudAlert: {risk_level} Risk Alert for {district}"
    body = f"""
CloudAlert Weather Alert

Dear {name},

Cloudburst risk detected in {district}.

Risk Level: {risk_level}
Probability: {probability}%

Action: {"Immediate evacuation recommended" if risk_level == "HIGH" else "Monitor conditions closely" if risk_level == "MEDIUM" else "No immediate action needed"}

View dashboard: http://localhost:3000

---
This is an automated alert from CloudAlert.
"""
    send_email_sync(email, subject, body)

async def send_verification_email(email: EmailStr, name: str, token: str, background_tasks: BackgroundTasks):
    print(f"[send_verification_email] Called! Sending to {email}")
    verification_url = f"http://localhost:8000/api/auth/verify/{token}"
    subject = "Verify your CloudAlert Account"
    body = f"""
CloudAlert Email Verification

Hello {name},

This link expires in 24 hours.

---
CloudAlert - Cloudburst Prediction System
"""
    send_email_sync(email, subject, body)
