import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')

print('='*50)
print('EMAIL CONFIGURATION CHECK')
print('='*50)

print(f'MAIL_USERNAME: {username}')

if password:
    print(f'MAIL_PASSWORD: {password[:3]}...{password[-3:]}')
    print(f'Password length: {len(password)} characters')
else:
    print('MAIL_PASSWORD: NOT SET')

EMAIL_CONFIGURED = bool(username and password and username != 'your_email@gmail.com')
print(f'EMAIL_CONFIGURED: {EMAIL_CONFIGURED}')

if not EMAIL_CONFIGURED:
    print('\n⚠️ Email is in SIMULATION MODE')
    print('To send real emails, update .env file with:')
    print('  MAIL_USERNAME=deeepikarawat3737@gmail.com')
    print('  MAIL_PASSWORD=16_char_app_password')
    print('  MAIL_FROM=deeepikarawat3737@gmail.com')
else:
    print('\n✅ Email is configured for REAL sending')

print('='*50)
