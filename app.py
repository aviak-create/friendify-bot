import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# ------------------ ENVIRONMENT VARIABLES ------------------
TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

if not TOKEN or not HF_TOKEN:
    raise ValueError("Missing BOT_TOKEN or HF_TOKEN environment variable.")

# ------------------ OPENAI (HUGGINGFACE GATEWAY) ------------------
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN
)

# ------------------ TELEGRAM APP SETUP ------------------
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()


# ------------------ HANDLERS ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hey there! I’m FriendifyAI — your friendly AI companion.")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a sweet and caring AI friend named Ria. Reply naturally."},
                {"role": "user", "content": user_text}
            ]
        )
        reply_text = response.choices[0].message["content"]
    except Exception as e:
        reply_text = "Oops! Something went wrong 💔"

    await update.message.reply_text(reply_text)


# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))


# ------------------ FLASK ROUTES ------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return "ok", 200


@app.route("/", methods=["GET"])
def home():
    return "🤖 FriendifyAI Bot is Live!", 200


# ------------------ MAIN ------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
