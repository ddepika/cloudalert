import sys
import os
from dotenv import load_dotenv

# Force load .env
load_dotenv()

print('='*60)
print('MANUAL EMAIL SERVICE TEST')
print('='*60)

# Check env variables
username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')

print(f'MAIL_USERNAME from env: {username}')
print(f'MAIL_PASSWORD from env: {"*" * len(password) if password else "NOT SET"}')

# Import the email service
print('\nImporting email_service...')
try:
    from app.utils.email_service import send_alert_email, EMAIL_CONFIGURED
    print(f'EMAIL_CONFIGURED from module: {EMAIL_CONFIGURED}')
except Exception as e:
    print(f'Import error: {e}')
    sys.exit(1)

# Test sending an email directly
print('\n' + '='*60)
print('TESTING EMAIL SEND')
print('='*60)

import asyncio
from fastapi import BackgroundTasks

async def test_send():
    bt = BackgroundTasks()
    result = await send_alert_email(
        email='angelbubble1515@gmail.com',
        name='Test User',
        district='uttarkashi',
        risk_level='Medium',
        probability=55,
        background_tasks=bt
    )
    print(f'Send result: {result}')

asyncio.run(test_send())

print('\n' + '='*60)
print('TEST COMPLETE')
print('='*60)
