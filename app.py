import os
import random
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===================== BOT CONFIG =====================
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
UPGRADE_LINK = "https://rzp.io/rzp/D0H2ymY7"
FREE_TEXT_LIMIT = 25
FREE_IMAGE_LIMIT = 2
VIP_TEXT_LIMIT = 9999  # unlimited
VIP_IMAGE_LIMIT = 5

# ===================== FLASK APP =====================
app = Flask(__name__)

# ===================== TELEGRAM APP =====================
telegram_app = Application.builder().token(TOKEN).build()

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO)

# ===================== DATA FILES =====================
DATA_FOLDER = "data"
BASIC_TEXT_FILE = os.path.join(DATA_FOLDER, "basic.txt")
VIP_TEXT_FILE = os.path.join(DATA_FOLDER, "vip.txt")
BASIC_IMAGES_FILE = os.path.join(DATA_FOLDER, "images_basic.txt")
VIP_IMAGES_FILE = os.path.join(DATA_FOLDER, "images_vip.txt")

def load_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

BASIC_REPLIES = load_file(BASIC_TEXT_FILE)
VIP_REPLIES = load_file(VIP_TEXT_FILE)
BASIC_IMAGES = load_file(BASIC_IMAGES_FILE)
VIP_IMAGES = load_file(VIP_IMAGES_FILE)

# ===================== DATA STORAGE =====================
# user_data structure: {user_id: {"tier": "free"/"vip", "texts": int, "images": int}}
user_data = {}

# ===================== KEYWORDS =====================
FLIRTY_KEYWORDS = ["sexy", "horny", "flirt", "kiss", "baby"]  # lowercase

# ===================== COMMAND HANDLER =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"tier": "free", "texts": 0, "images": 0}
    await update.message.reply_text(
        "💞 Welcome to Friendify AI!\n"
        "You need to pay 49₹ to start chatting.\n"
        f"Upgrade here 👉 {UPGRADE_LINK}"
    )

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if user_id not in user_data:
        # Force user to pay first
        await update.message.reply_text(
            f"💔 You cannot chat without subscribing.\nPay 49₹ here 👉 {UPGRADE_LINK}"
        )
        return

    user_info = user_data[user_id]

    # Check if flirty keyword used
    if any(k in text for k in FLIRTY_KEYWORDS):
        user_info["tier"] = "vip"
        user_info["texts"] = 0
        user_info["images"] = 0
        await update.message.reply_text(
            f"🔥 Flirty message detected! You've unlocked VIP for today.\n{UPGRADE_LINK}"
        )
        return

    # Determine tier limits
    if user_info["tier"] == "free":
        limit_texts = FREE_TEXT_LIMIT
        replies_list = BASIC_REPLIES
    else:
        limit_texts = VIP_TEXT_LIMIT
        replies_list = VIP_REPLIES

    # Check text limit
    if user_info["texts"] >= limit_texts:
        await update.message.reply_text(
            f"💔 You’ve reached your daily text limit.\nUpgrade VIP for more 💕\n{UPGRADE_LINK}"
        )
        return

    # Increment text counter and reply
    user_info["texts"] += 1
    reply = random.choice(replies_list)
    await update.message.reply_text(reply)

# ===================== IMAGE HANDLER =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_data:
        await update.message.reply_text(
            f"💔 You cannot send images without subscribing.\nPay 49₹ here 👉 {UPGRADE_LINK}"
        )
        return

    user_info = user_data[user_id]

    if user_info["tier"] == "free":
        limit_images = FREE_IMAGE_LIMIT
        images_list = BASIC_IMAGES
    else:
        limit_images = VIP_IMAGE_LIMIT
        images_list = VIP_IMAGES

    if user_info["images"] >= limit_images:
        await update.message.reply_text(
            f"📸 You’ve reached your daily image limit.\nUpgrade VIP for more 💕\n{UPGRADE_LINK}"
        )
        return

    # Increment image counter and reply with random image
    user_info["images"] += 1
    if images_list:
        reply_image = random.choice(images_list)
        await update.message.reply_text(f"Here you go! {reply_image}")
    else:
        await update.message.reply_text("😍 Wow! You look amazing!")

# ===================== ADD HANDLERS =====================
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ===================== FLASK WEBHOOK =====================
@app.route("/")
def home():
    return "Friendify AI Bot is live 💖"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    from asyncio import get_event_loop

    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    loop = get_event_loop()
    loop.create_task(telegram_app.process_update(update))
    return "ok"

# ===================== MAIN =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Starting bot on port {port}")
    telegram_app.bot.set_webhook(f"https://friendify-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=port)
