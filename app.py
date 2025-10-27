import os
from flask import Flask, request
import requests
from dotenv import load_dotenv

# Load .env file if running locally or on Render
load_dotenv()

# Fetch tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# Check for missing tokens
if not BOT_TOKEN or not HF_TOKEN:
    raise ValueError("Missing BOT_TOKEN or HF_TOKEN environment variable.")

# Telegram API URL
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Flask app
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "🤖 FriendifyAI Bot is running successfully on Render!"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user_text = update["message"]["text"]

        # Hugging Face API request
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": user_text}

        try:
            hf_response = requests.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json=payload,
                timeout=15
            )
            result = hf_response.json()

            # Extract response text safely
            if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
                reply = result[0]["generated_text"]
            else:
                reply = "I'm here! Let's chat ❤️"

        except Exception as e:
            reply = f"Error: {e}"

        # Send reply back to Telegram
        send_url = f"{TELEGRAM_URL}/sendMessage"
        requests.post(send_url, json={"chat_id": chat_id, "text": reply})

    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render uses dynamic ports
    app.run(host="0.0.0.0", port=port)
