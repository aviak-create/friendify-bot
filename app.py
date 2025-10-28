import os
import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters, CallbackContext
import requests

# --- Environment Variables ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not TELEGRAM_TOKEN or not HF_TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN or HF_TOKEN environment variables.")

# --- Flask & Telegram Bot Setup ---
app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# Logging setup for debugging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- Hugging Face AI Reply Function ---
def generate_ai_reply(user_message: str) -> str:
    """
    Sends the user message to Hugging Face model and returns the generated reply.
    """
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    data = {
        "inputs": f"You are Ria, a caring and romantic AI girlfriend. Reply warmly to: {user_message}",
    }
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers=headers,
            json=data,
            timeout=30
        )
        result = response.json()
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"]
        else:
            return "💞 I'm here for you, darling. Tell me more!"
    except Exception as e:
        logging.error(f"Hugging Face API error: {e}")
        return "🌸 Something went wrong, love!"

# --- Telegram Message Handler ---
def handle_message(update: Update, context: CallbackContext):
    user_text = update.message.text
    reply_text = generate_ai_reply(user_text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

# --- Flask Webhook Route ---
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok", 200

# --- Home Route ---
@app.route("/", methods=["GET"])
def home():
    return "💖 FriendifyAI Bot is Live on Railway!"

# --- Telegram Dispatcher Setup ---
from telegram.ext import Dispatcher
dispatcher = Dispatcher(bot, None, use_context=True)
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# --- Run Flask App ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
