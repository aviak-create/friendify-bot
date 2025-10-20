import os
import random
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===================== BOT CONFIG =====================
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"
UPGRADE_LINK = "https://rzp.io/rzp/D0H2ymY7"
FREE_MESSAGE_LIMIT = 25
FREE_IMAGE_LIMIT = 2

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO)

# ===================== SAMPLE REPLIES =====================
BASIC_REPLIES = [
    "Hehe, you’re cute 😘",
    "Aww that’s sweet 💞",
    "Tell me more, I’m listening 👀",
    "Haha, you make me smile 😍",
    "You’re too adorable 💋",
    "Really? That’s interesting 😉",
    "You’re fun to talk to 💕",
    "I love this chat already 😌",
    "Haha stop it, you’re making me blush 🥰",
]

# ===================== DATA STORAGE =====================
user_data = {}

# ===================== COMMAND HANDLER =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {"messages": 0, "images": 0}
    await update.message.reply_text(
        "💞 Welcome to Friendify AI!\n"
        "You can chat with your AI partner here.\n\n"
        "You have 25 free messages & 2 free image responses.\n"
        f"To unlock unlimited messages, upgrade here 👉 {UPGRADE_LINK}"
    )
    logging.info(f"/start used by {user_id}")

# ===================== MESSAGE HANDLER =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        text = update.message.text
        logging.info(f"Message from {user_id}: {text}")

        if user_id not in user_data:
            user_data[user_id] = {"messages": 0, "images": 0}

        user_info = user_data[user_id]

        if user_info["messages"] >= FREE_MESSAGE_LIMIT:
            await update.message.reply_text(
                f"💔 You’ve reached your 25 free messages.\n\n"
                f"Upgrade now for unlimited chat & more images 💕\n"
                f"{UPGRADE_LINK}"
            )
            return

        user_info["messages"] += 1
        reply = random.choice(BASIC_REPLIES)
        await update.message.reply_text(f"💬 Friendify AI: {reply}")

    except Exception as e:
        logging.error(f"Error in handle_message: {e}")

# ===================== IMAGE HANDLER =====================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        logging.info(f"Photo received from {user_id}")

        if user_id not in user_data:
            user_data[user_id] = {"messages": 0, "images": 0}

        user_info = user_data[user_id]

        if user_info["images"] >= FREE_IMAGE_LIMIT:
            await update.message.reply_text(
                f"📸 You’ve used your 2 free images.\n\n"
                f"Upgrade to unlock more images & romantic content 💕\n"
                f"{UPGRADE_LINK}"
            )
            return

        user_info["images"] += 1
        await update.message.reply_text("😍 Wow! You look amazing in this one!")

    except Exception as e:
        logging.error(f"Error in handle_photo: {e}")

# ===================== SETUP TELEGRAM APP =====================
telegram_app = Application.builder().token(TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ===================== RUN WEBHOOK =====================
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))
    logging.info(f"Starting bot on port {PORT}")

    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://friendify-bot.onrender.com/{TOKEN}"
    )
