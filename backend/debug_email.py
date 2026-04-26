import os
import smtplib
from dotenv import load_dotenv

load_dotenv()

print('='*50)
print('EMAIL DEBUG')
print('='*50)

username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')

print(f'MAIL_USERNAME: {username}')

if password:
    print(f'MAIL_PASSWORD exists: Yes')
    print(f'Password length: {len(password)} characters')
    print(f'Password first 4 chars: {password[:4]}')
else:
    print('MAIL_PASSWORD: NOT SET')

# Check if password is the placeholder
if password and password == 'your_16_char_app_password_without_spaces':
    print('⚠️ You are still using the PLACEHOLDER password!')
    print('Please replace it with your actual 16-character App Password')
    print('Get it from: https://myaccount.google.com/apppasswords')

EMAIL_CONFIGURED = bool(username and password and password != 'your_16_char_app_password_without_spaces')
print(f'EMAIL_CONFIGURED: {EMAIL_CONFIGURED}')

if EMAIL_CONFIGURED:
    print('\nTesting SMTP connection...')
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)
        print('✅ SMTP LOGIN: SUCCESSFUL')
        print('Your email is ready to send real messages!')
        server.quit()
    except Exception as e:
        print(f'❌ SMTP LOGIN FAILED: {e}')
else:
    print('\n❌ Email NOT configured properly')
    print('Please update your .env file with:')
    print('  MAIL_USERNAME=deeepikarawat3737@gmail.com')
    print('  MAIL_PASSWORD=your_16_char_app_password')
    print('  MAIL_FROM=deeepikarawat3737@gmail.com')

print('='*50)
