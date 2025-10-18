import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import os

# ---------------- BOT TOKEN ---------------- #
TOKEN = "8286419006:AAFQ7Pj0qDvt4wc7CdjdgOq59ZGS5pI5pUo"

# ---------------- TELEGRAM HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hey there! 👋 I'm your Friendify bot, ready to chat!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Just send me a message and I’ll reply!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"You said: {text}")

# ---------------- TELEGRAM BOT MAIN FUNCTION ---------------- #
async def run_bot():
    print("🚀 Starting Friendify Bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Initialize and start polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("🤖 Bot is polling...")
    await asyncio.Event().wait()  # Keep the bot alive

# ---------------- SIMPLE HTTP SERVER FOR RENDER ---------------- #
PORT = int(os.environ.get("PORT", 10000))  # Render provides PORT env variable

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Friendify Bot is running!")

def start_server():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"🌐 HTTP server running on port {PORT}")
    server.serve_forever()

# Start HTTP server in a separate thread
threading.Thread(target=start_server, daemon=True).start()

# ---------------- ENTRY POINT ---------------- #
if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Schedule the bot task on the existing loop
    loop.create_task(run_bot())

    # Keep the script alive
    loop.run_forever()
