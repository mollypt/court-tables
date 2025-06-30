import os
import requests

webhook = os.getenv("CHAT_WEBHOOK")

if not webhook:
    raise ValueError("CHAT_WEBHOOK not set!")

message = {"text": "🤖 Hello from GitHub Actions!"}
response = requests.post(webhook, json=message)
response.raise_for_status()

print("Message sent!")
