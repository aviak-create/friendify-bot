from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Environment variable for Razorpay secret
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")

# Free limits
FREE_TEXT_LIMIT = 25
FREE_IMAGE_LIMIT = 2

# Store user counts in memory (temporary, will reset if server restarts)
user_data = {}

WELCOME_MESSAGE = """Welcome to Friendify AI 🤖
You get 25 text messages + 2 images free.
After that, upgrade for more."""

UPGRADE_LINK = "https://rzp.io/rzp/wtTrLSAY"  # Your ₹69 upgrade link

# Telegram Bot token
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")

        # Initialize user if new
        if chat_id not in user_data:
            user_data[chat_id] = {"texts": 0, "images": 0}

            # Send welcome message
            send_message(chat_id, WELCOME_MESSAGE)
            return {"ok": True}

        # Update text count
        user_data[chat_id]["texts"] += 1

        # Check limits
        if user_data[chat_id]["texts"] > FREE_TEXT_LIMIT or user_data[chat_id]["images"] > FREE_IMAGE_LIMIT:
            send_message(chat_id, f"You reached your free limit. Upgrade here: {UPGRADE_LINK}")
        else:
            send_message(chat_id, f"Received: {user_text} ✅ You have {FREE_TEXT_LIMIT - user_data[chat_id]['texts']} free texts left.")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
