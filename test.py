import requests
import os

def main():
    webhook = "https://chat.googleapis.com/v1/spaces/AAQAxB19qsI/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=x1jm_T3upSzsog2RuS1egFb2pF-g2O_5jivVoau9Q1k"
    if not webhook:
        raise ValueError("CHAT_WEBHOOK environment variable is missing.")

    message = {"text": "🤖 Hello from Render! This is your scheduled message."}
    response = requests.post(webhook, json=message)
    response.raise_for_status()

    print("Message sent successfully.")

if __name__ == "__main__":
    main()
