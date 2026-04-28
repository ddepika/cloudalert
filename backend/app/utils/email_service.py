import os
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@cloudalert.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True if os.getenv("MAIL_USERNAME") else False,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, name: str, token: str, background_tasks: BackgroundTasks):
    verification_url = f"http://localhost:8000/api/auth/verify/{token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; }}
            .header {{ background: #012060; color: white; padding: 20px; text-align: center; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #012060; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CloudAlert</h1>
                <p>Cloudburst Prediction System</p>
            </div>
            <div class="content">
                <h2>Hello {name}!</h2>
                <p>Please click the button below to verify your email:</p>
                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Verify Email</a>
                </div>
                <p>This link is valid for 30 days.</p>
            </div>
            <div class="footer">
                <p>CloudAlert - Cloudburst Prediction System</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Verify your CloudAlert Account",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    
    if os.getenv("MAIL_USERNAME"):
        background_tasks.add_task(fm.send_message, message)
        print(f"Verification email sent to {email}")
        return {"sent": True}
    else:
        print(f"\n{'='*60}")
        print(f"EMAIL NOT CONFIGURED")
        print(f"Verification link for {email}: {verification_url}")
        print(f"{'='*60}\n")
        return {"sent": False, "link": verification_url}

async def send_alert_email(email: EmailStr, name: str, district: str, risk_level: str, probability: float, background_tasks: BackgroundTasks):
    risk_color = "#d32f2f" if risk_level == "HIGH" else "#ff9800" if risk_level == "MEDIUM" else "#4caf50"
    
    action_message = "Immediate evacuation recommended" if risk_level == "HIGH" else "Monitor conditions closely"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: auto; }}
            .alert {{ background: {risk_color}; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="alert">
                <h1>CloudAlert</h1>
                <h2>{risk_level} RISK ALERT</h2>
            </div>
            <div class="content">
                <h2>Dear {name},</h2>
                <p>A potential cloudburst event has been detected in <strong>{district}</strong>.</p>
                <p><strong>Risk Probability:</strong> {probability}%</p>
                <p><strong>Risk Level:</strong> {risk_level}</p>
                <p><strong>Suggested Action:</strong> {action_message}</p>
                <p>Stay safe and follow local authorities.</p>
            </div>
            <div class="footer">
                <p>This is an automated alert from CloudAlert System.</p>
                
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject=f"CloudAlert: {risk_level} Risk Alert for {district}",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    
    if os.getenv("MAIL_USERNAME"):
        background_tasks.add_task(fm.send_message, message)
        print(f"Alert email sent to {email}")
    else:
        print(f"\n{'='*60}")
        print(f"EMAIL NOT CONFIGURED - Alert for {email}")
        print(f"District: {district}, Risk: {risk_level} ({probability}%)")
        print(f"{'='*60}\n")
