import secrets
import os

# Generate a secure random key
key = secrets.token_hex(32)

# Save to .env file
with open('.env', 'w') as f:
    f.write(f'API_KEY={key}\n')
    f.write(f'FLASK_PORT=5000\n')
    f.write(f'FLASK_DEBUG=True\n')

print("=" * 50)
print("API Key Generated Successfully!")
print("=" * 50)
print(f"Your API Key: {key}")
print()
print(".env file created in your project folder")
print()
print("Copy this key and paste in config.js file:")
print(f"API_KEY: '{key}'")
print("=" * 50)