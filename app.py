import os
import json
import random
from flask import Flask, request
from telegram import Bot

app = Flask(__name__)

# Telegram bot token from Render environment variable
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

# --- Load message data ---
with open("data/basic.json", "r", encoding="utf-8") as f:
    BASIC = json.load(f)
with open("data/vip.json", "r", encoding="utf-8") as f:
    VIP = json.load(f)

# --- User data store ---
# chat_id : {"plan": "basic"/"vip", "messages_used": int, "images_used": int}
user_data = {}

# Lusty/horny keywords
lusty_keywords = ["horny", "lust", "sexy", "intimate", "naked"]

# Payment links
PAYMENT_LINK_49 = "https://rzp.io/rzp/39ETVZ1"
UPGRADE_LINK_119 = "https://rzp.io/rzp/DMsjkvt"
VIP_LINK_199 = "https://rzp.io/rzp/qgH40oy"

@app.route("/")
def home():
    return "Friendify AI Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "ok"

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "").lower().strip()

    # --- Step 1: enforce payment ---
    if chat_id not in user_data:
        # Assume user paid 49₹ before entering Telegram (we only allow 49₹ initially)
        # Here you can integrate actual payment verification if needed
        user_data[chat_id] = {"plan": "basic", "messages_used": 0, "images_used": 0}
        bot.send_message(chat_id, f"🎉 Welcome to Friendify AI! You have 25 messages + 2 images in your 49₹ pack.\nStart chatting now!")
        return "ok"

    user = user_data[chat_id]

    # --- Step 2: check for lusty/horny text ---
    if any(word in text for word in lusty_keywords):
        if user["plan"] == "basic":
            bot.send_message(chat_id, f"🔥 For intimate chats, upgrade to VIP 199₹ here: {VIP_LINK_199}")
            return "ok"

    # --- Step 3: check pack limits ---
    if user["plan"] == "basic":
        if user["messages_used"] >= 25 and user["images_used"] >= 2:
            bot.send_message(chat_id, f"💌 Your 49₹ pack is over. Upgrade to 119₹ for more messages and images: {UPGRADE_LINK_119}")
            return "ok"

    # --- Step 4: send response (text or image) ---
    content = BASIC if user["plan"] == "basic" else VIP

    if random.random() < 0.8:  # 80% chance text
        msg = random.choice(content["messages"])
        bot.send_message(chat_id, msg)
        if user["plan"] == "basic":
            user["messages_used"] += 1
    else:  # 20% chance image
        img = random.choice(content["images"])
        bot.send_photo(chat_id, photo=img)
        if user["plan"] == "basic":
            user["images_used"] += 1

    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
