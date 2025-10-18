import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo")

# ---------------- HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey there! 👋 I'm your Friendify bot, ready to chat!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just send me a message and I’ll reply!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

# ---------------- MAIN FUNCTION ---------------- #
async def main():
    print("🚀 Starting Friendify Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

# ---------------- ENTRY POINT ---------------- #
if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
        print("⚙️ Using existing event loop (Render safe)")
        loop.create_task(main())
        loop.run_forever()
    except RuntimeError:
        print("🌀 Creating new event loop (Local safe)")
        asyncio.run(main())
