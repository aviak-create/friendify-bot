from flask import Flask, request
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
UPGRADE_LINK = "https://rzp.io/rzp/wtTrLSAY"

# Memory to track user message counts
user_data = {}

@app.route('/')
def home():
    return "Friendify AI Bot is running successfully!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = request.get_json()

    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        user_message = update["message"].get("text", "")
        user = user_data.get(chat_id, {"messages": 0, "images": 0})

        if user["messages"] < 25:
            user["messages"] += 1
            user_data[chat_id] = user
            send_message(chat_id, f"❤️ Hey there! I’m Friendify — your AI companion.\n\nYou’ve used {user['messages']} of 25 free messages.\nAsk me anything 😉")
        else:
            send_message(chat_id, f"✨ You’ve used your 25 free messages + 2 images.\nUpgrade now for unlimited fun — ₹69 only!\n\n👉 [Upgrade Now]({UPGRADE_LINK})")

    elif "photo" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        user = user_data.get(chat_id, {"messages": 0, "images": 0})

        if user["images"] < 2:
            user["images"] += 1
            user_data[chat_id] = user
            send_message(chat_id, f"📸 You’ve used {user['images']} of 2 free images.")
        else:
            send_message(chat_id, f"⚡ Your free image limit is over.\nUpgrade now for 5 premium AI images for just ₹69.\n\n👉 [Upgrade Now]({UPGRADE_LINK})")

    return "ok", 200

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
