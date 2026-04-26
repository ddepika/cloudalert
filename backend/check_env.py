from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv('MAIL_USERNAME')
password = os.getenv('MAIL_PASSWORD')

print('='*50)
print('ENV FILE CHECK')
print('='*50)
print(f'MAIL_USERNAME: {username}')
print(f'MAIL_PASSWORD length: {len(password) if password else 0}')
print(f'MAIL_PASSWORD first 3 chars: {password[:3] if password else "None"}')
print(f'MAIL_PASSWORD last 3 chars: {password[-3:] if password else "None"}')
print('='*50)
print(f'Has valid credentials: {bool(username and password)}')
