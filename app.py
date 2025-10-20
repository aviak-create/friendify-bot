import os
import random
import logging
from datetime import date
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===================== CONFIG =====================
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
UPGRADE_LINK_49 = "https://rzp.io/rzp/D0H2ymY7"   # 49₹ link
UPGRADE_LINK_119 = "https://rzp.io/rzp/D0H2ymY7"  # 119₹ link
DAILY_MESSAGE_LIMIT = 25
DAILY_IMAGE_LIMIT = 2
VIP_IMAGE_LIMIT = 5

FLIRTY_KEYWORDS = ["sexy", "horny", "hot", "naughty", "kiss", "fuck", "seduce"]

# ===================== FLASK APP =====================
app = Flask(__name__)

# ===================== TELEGRAM APP =====================
telegram_app = Application.builder().token(TOKEN).build()

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO)

# ===================== USER DATA =====================
user_data = {}  # {user_id: {"messages":0,"images":0,"tier":"basic/vip","last_payment_day":date}}

# ===================== HELPERS =====================
def get_text_reply(user_info):
    if user_info["tier"] == "vip":
        file = "data/vip.txt"
    else:
        file = "data/basic.txt"
    with open(file) as f:
        replies = f.read().splitlines()
    return random.choice(replies)

def get_image_url(user_info):
    if user_info["tier"] == "vip":
        limit = VIP_IMAGE_LIMIT
        file = "data/images_vip.txt"
    else:
        limit = DAILY_IMAGE_LIMIT
        file = "data/images_basic.txt"

    if user_info["images"] >= limit:
        return None

    with open(file) as f:
        urls = f.read().splitlines()
    user_info["images"] += 1
    return random.choice(urls)

def reset_daily(user_info):
    today = date.today()
    if user_info.get("last_payment_day") != today:
        user_info["messages"] = 0
        user_info["images"] = 0
        user_info["last_payment_day"] = today

# ===================== COMMAND HANDLER =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"messages":0,"images":0,"tier":None,"last_payment_day":None}

    await update.message.reply_text(
        f"💞 Welcome to Friendify AI!\n"
        f"You need to pay 49₹ to start chatting.\n"
        f"Pay here 👉 {UPGRADE_LINK_49}"
    )

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        user_data[user_id] = {"messages":0,"images":0,"tier":None,"last_payment_day":None}
    
    user_info = user_data[user_id]

    # ====== Paid check ======
    if user_info["tier"] is None:
        await update.message.reply_text(
            f"💳 You must pay 49₹ to start chatting.\nPay here 👉 {UPGRADE_LINK_49}"
        )
        return

    # ====== Reset daily ======
    reset_daily(user_info)

    # ====== Flirty trigger ======
    if any(word in text.lower() for word in FLIRTY_KEYWORDS):
        user_info["tier"] = "vip"
        user_info["messages"] = 0
        user_info["images"] = 0
        user_info["last_payment_day"] = date.today()
        await update.message.reply_text(
            f"🔥 Flirty detected! You’re now VIP for today with unlimited chat & 5 images 💕\n{UPGRADE_LINK_119}"
        )
        return

    # ====== Check message limit for basic ======
    if user_info["tier"] == "basic" and user_info["messages"] >= DAILY_MESSAGE_LIMIT:
        await update.message.reply_text(
            f"💬 You’ve reached your 25 messages limit for today.\n"
            f"Upgrade to VIP 119₹ for unlimited messages & 5 images 💕\n{UPGRADE_LINK_119}"
        )
        return

    # ====== Send reply ======
    user_info["messages"] += 1
    reply = get_text_reply(user_info)
    await update.message.reply_text(f"💬 Friendify AI: {reply}")

# ===================== IMAGE HANDLER =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"messages":0,"images":0,"tier":None,"last_payment_day":None}

    user_info = user_data[user_id]

    if user_info["tier"] is None:
        await update.message.reply_text(
            f"💳 You must pay 49₹ to use images.\nPay here 👉 {UPGRADE_LINK_49}"
        )
        return

    reset_daily(user_info)

    url = get_image_url(user_info)
    if not url:
        await update.message.reply_text(
            f"📸 You’ve used all your images for today.\nUpgrade to VIP 119₹ for 5 images/day 💕\n{UPGRADE_LINK_119}"
        )
        return

    await update.message.reply_text(url)

# ===================== ADD HANDLERS =====================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ===================== FLASK ROUTES =====================
@app.route("/")
def home():
    return "Friendify AI Bot is live 💖"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

# ===================== MAIN =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://friendify-bot.onrender.com/{TOKEN}"
    )
