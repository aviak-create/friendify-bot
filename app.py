import os
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from openai import OpenAI

# Load tokens from environment variables (Render -> Environment)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL")

# Init AI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Init Telegram objects
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)
tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Bot handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": user_text}]
        )

        reply = completion.choices[0].message.content
    except Exception as e:
        reply = "⚠️ Error talking to AI. Try again!"

    await update.message.reply_text(reply)

# Bind handler
tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Flask route for Telegram Webhook
@app.post("/webhook")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await tg_app.process_update(update)
    return "OK"

# Set webhook
async def set_webhook():
    await bot.delete_webhook()
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

# Run server
if __name__ == "__main__":
    print("🚀 Starting Telegram bot on Render...")
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=10000)
