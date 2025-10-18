import asyncio
import os
import json
import random
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer

# ---------------- BOT TOKEN ---------------- #
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"

# ---------------- DATA LOADING ---------------- #
with open("data/basic.json", "r", encoding="utf-8") as f:
    BASIC_REPLIES = json.load(f)

with open("data/vip.json", "r", encoding="utf-8") as f:
    VIP_REPLIES = json.load(f)

# ---------------- USER DATA ---------------- #
# Tracks messages/images sent per user
USER_STATS = {}  # {user_id: {"type":"49"/"119"/"vip","msg_count":int,"img_count":int}}

# Payment links
PACK_49_LINK = "https://friendifyai.netlify.app"  # 49 pack landing page
PACK_119_LINK = "https://rzp.io/rzp/D0H2ymY7"     # 119 pack Razorpay link

# Keywords triggering instant 119 upgrade
FLIRTY_KEYWORDS = ["horny", "flirty", "sex", "nude", "intimate"]  

# VIP users example
VIP_USERS = [123456789]  # Telegram user_ids

# ---------------- TELEGRAM HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in VIP_USERS:
        USER_STATS[user_id] = {"type": "vip", "msg_count": 0, "img_count": 0}
        await update.message.reply_text("Welcome VIP! Enjoy unlimited chatting 😎")
    else:
        # default: new user = 49 pack
        USER_STATS[user_id] = {"type": "49", "msg_count": 0, "img_count": 0}
        await update.message.reply_text(
            "Welcome! You have 25 messages + 2 images. Upgrade to 119 pack for full access."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send messages or images to chat with Friendify AI!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower() if update.message.text else ""
    user = USER_STATS.get(user_id, {"type":"49","msg_count":0,"img_count":0})

    # Detect flirty keywords for 49 pack users
    if user["type"] in ["49"] and any(word in text for word in FLIRTY_KEYWORDS):
        await update.message.reply_text(
            f"⚠️ For intimate/flirty messages, please upgrade to 119 pack: {PACK_119_LINK}"
        )
        return

    # Count messages for 49 pack
    if user["type"] == "49" and update.message.text:
        user["msg_count"] += 1

    # Count images
    if update.message.photo:
        user["img_count"] += 1

    # Check if 49 pack limits reached (25 msgs + 2 images)
    if user["type"] == "49" and (user["msg_count"] > 25 or user["img_count"] > 2):
        await update.message.reply_text(
            f"🎁 You have reached your 49 pack limit. Upgrade to 119 pack to continue: {PACK_119_LINK}"
        )
        return

    # Select reply
    if user["type"] == "vip":
        reply = random.choice(VIP_REPLIES)
    else:
        reply = random.choice(BASIC_REPLIES)

    # Save updated stats
    USER_STATS[user_id] = user

    await update.message.reply_text(reply)

# ---------------- TELEGRAM BOT MAIN FUNCTION ---------------- #
async def run_bot():
    print("🚀 Starting Friendify Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_message))  # handle images

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("🤖 Bot is polling...")
    await asyncio.Event().wait()  # Keep alive

# ---------------- SIMPLE HTTP SERVER FOR RENDER ---------------- #
PORT = int(os.environ.get("PORT", 10000))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Friendify Bot is running!")

def start_server():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"🌐 HTTP server running on port {PORT}")
    server.serve_forever()

threading.Thread(target=start_server, daemon=True).start()

# ---------------- ENTRY POINT ---------------- #
if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.create_task(run_bot())
    loop.run_forever()
