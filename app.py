import json
import random
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# -----------------------------
# Configuration
# -----------------------------
TELEGRAM_TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
UPGRADE_LINK = "https://rzp.io/rzp/D0H2ymY7"
MAX_BASIC_MESSAGES = 25
MAX_BASIC_IMAGES = 2

# Lusty/horny keywords
HORNY_KEYWORDS = [
    "horny", "lust", "sexy", "naughty", "intimate", "fuck", "cum",
    "cock", "boobs", "pussy", "dick", "sex", "hot"
]

# -----------------------------
# Load JSON message packs
# -----------------------------
with open("data/basic.json", "r", encoding="utf-8") as f:
    basic_pack = json.load(f)

with open("data/vip.json", "r", encoding="utf-8") as f:
    vip_pack = json.load(f)

# -----------------------------
# User tracking
# -----------------------------
paid_users = {}  # {user_id: {"pack": "basic"/"vip", "used_msgs": int, "used_imgs": int}}

# -----------------------------
# Helpers
# -----------------------------
async def check_paid(update: Update):
    user_id = str(update.effective_user.id)
    if user_id not in paid_users:
        await update.message.reply_text(
            "💌 You need to pay ₹49 first to chat with me!\nVisit our website to get started."
        )
        return False
    return True

def get_random_reply(pack):
    messages = pack.get("messages", [])
    return random.choice(messages) if messages else "🤖"

def get_random_image(pack):
    images = pack.get("images", [])
    return random.choice(images) if images else None

def is_horny(message_text):
    text = message_text.lower()
    return any(word in text for word in HORNY_KEYWORDS)

async def send_upgrade_prompt(update: Update):
    msg = f"""💌 Your pack has ended or restricted for intimate chats!  
Want to continue our fun & steamy chat? 😉  
Upgrade to VIP for unlimited messages & special content 🔥  
💳 Buy Now ₹119 → {UPGRADE_LINK}"""
    await update.message.reply_text(msg)

# -----------------------------
# Handlers
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in paid_users:
        paid_users[user_id] = {"pack": "basic", "used_msgs": 0, "used_imgs": 0}

    await update.message.reply_text(
        "Welcome to Friendify AI 🤖\nYou get 25 text messages + 2 images in your starter pack! Enjoy!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_paid(update):
        return

    user_id = str(update.effective_user.id)
    user_data = paid_users[user_id]

    if user_data["pack"] == "basic" and is_horny(update.message.text):
        await send_upgrade_prompt(update)
        return

    if user_data["pack"] == "basic" and user_data["used_msgs"] >= MAX_BASIC_MESSAGES:
        await send_upgrade_prompt(update)
        return

    pack = basic_pack if user_data["pack"] == "basic" else vip_pack
    reply_text = get_random_reply(pack)
    await update.message.reply_text(reply_text)

    if user_data["pack"] == "basic":
        user_data["used_msgs"] += 1
        if user_data["used_imgs"] < MAX_BASIC_IMAGES:
            img_url = get_random_image(pack)
            if img_url:
                await update.message.reply_photo(img_url)
                user_data["used_imgs"] += 1

async def upgrade_to_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_paid(update):
        return

    user_id = str(update.effective_user.id)
    paid_users[user_id]["pack"] = "vip"
    await update.message.reply_text(
        "🎉 You are now VIP! Enjoy unlimited chats and images 😘"
    )

# -----------------------------
# Main
# -----------------------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", upgrade_to_vip))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
