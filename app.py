import os
from telegram.ext import Application, MessageHandler, filters
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing BOT_TOKEN or OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

async def handle_message(update, context):
    user_text = update.message.text

    # Reply instantly
    await update.message.reply_text("💬 Typing...")

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are RIA, a sweet romantic girlfriend."},
            {"role": "user", "content": user_text}
        ]
    )

    reply = response.choices[0].message["content"]
    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
