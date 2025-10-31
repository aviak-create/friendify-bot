import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Telegram bot
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Friendify AI 👋💬\nHow can I help you today?")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_msg}]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

# Flask route for Telegram webhook
@app.route("/", methods=["GET"])
def home():
    return "Friendify AI Bot is Live!"

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200

async def run_bot():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()  # Optional - ensures background polling fallback

import asyncio
asyncio.get_event_loop().run_until_complete(run_bot())
