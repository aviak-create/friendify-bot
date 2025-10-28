import os
import logging
from flask import Flask, request
from openai import OpenAI
from telegram import Bot, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Dispatcher

app = Flask(__name__)

# Logging
logging.basicConfig(level=logging.INFO)

# Environment Variables
TOKEN = os.environ.get("BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PORT = int(os.environ.get("PORT", 8080))

bot = Bot(token=TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# Flask route for Telegram webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp = Dispatcher(bot, None, workers=0)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.process_update(update)
    return "ok"

# Handle messages
def handle_message(update, context=None):
    user_text = update.message.text
    chat_id = update.message.chat.id

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}],
        )
        reply = response.choices[0].message["content"]
    except Exception as e:
        reply = "⚠️ Sorry, something went wrong."

    bot.send_message(chat_id=chat_id, text=reply)

@app.route("/", methods=["GET"])
def home():
    return "Friendify AI Telegram Bot is live!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
