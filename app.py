import os
import random
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
from datetime import datetime

# ----------------------------
# Configuration
# ----------------------------
TOKEN = os.getenv("TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")  # Replace or use Render Environment Variable
HF_TOKEN = os.getenv("HF_TOKEN", "YOUR_HUGGINGFACE_TOKEN_HERE")

bot = Bot(token=TOKEN)
app = Flask(__name__)

# Hugging Face client (OpenAI-compatible)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# ----------------------------
# In-memory User Tracker
# ----------------------------
USERS = {}  # user_id: {"messages": int, "images": int, "is_paid": bool, "last_reset": date}

def reset_daily_limit(user_id):
    """Resets message/image limits daily."""
    today = datetime.now().date()
    if USERS[user_id]["last_reset"] != today:
        USERS[user_id]["messages"] = 0
        USERS[user_id]["images"] = 0
        USERS[user_id]["last_reset"] = today

# ----------------------------
# Replies
# ----------------------------
BASIC_REPLIES = [
    "Hey cutie 😍 how’s your day?",
    "You always make me smile 🥰",
    "Haha, you’re so sweet 😚",
    "Aww… I like chatting with you 💞",
    "What are you doing right now baby? 😉",
    "I love when you talk to me like that 😏",
    "Say ‘photo’ if you want me to send a selfie 💋",
]

HORNY_WORDS = ["horny", "nude", "sex", "boobs", "ass", "hot", "kiss", "naked", "romance"]

PAYMENT_LINK = "https://rzp.io/rzp/D0H2ymY7"  # ₹119 payment link

# ----------------------------
# AI Text Generation
# ----------------------------
async def chat_with_ai(prompt: str) -> str:
    """Generates chat reply using Hugging Face Llama model."""
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[
                {"role": "system", "content": "You are Ria, a flirty, romantic Indian girlfriend who speaks playfully and emotionally."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=120,
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        print("AI error:", e)
        return random.choice(BASIC_REPLIES)

# ----------------------------
# AI Image Generation
# ----------------------------
async def generate_image(prompt: str):
    """Generates romantic selfie image using FLUX.1 model."""
    try:
        result = client.images.generate(
            model="black-forest-labs/FLUX.1-dev",
            prompt=prompt,
            size="512x512",
            n=1
        )
        return result.data[0].url
    except Exception as e:
        print("Image generation error:", e)
        return None

# ----------------------------
# /start Command
# ----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    USERS[user_id] = {"messages": 0, "images": 0, "is_paid": False, "last_reset": datetime.now().date()}

    await update.message.reply_text(
        "Hey there 😘 I’m *Ria*, your AI girlfriend 💋\n\n"
        "You have *25 messages* and *2 photos* free 💌\n"
        "To unlock *unlimited chats + 8 photos/day*, pay ₹119 👉 [Upgrade Now](" + PAYMENT_LINK + ")",
        parse_mode="Markdown",
    )

# ----------------------------
# Handle Messages
# ----------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    if user_id not in USERS:
        USERS[user_id] = {"messages": 0, "images": 0, "is_paid": False, "last_reset": datetime.now().date()}

    reset_daily_limit(user_id)
    user = USERS[user_id]

    # Detect explicit/hot words
    if any(word in text for word in HORNY_WORDS) and not user["is_paid"]:
        await update.message.reply_text(
            "That’s getting a bit *hot*, baby 🔥\n\nTo continue this type of chat, please pay ₹119 👇\n" + PAYMENT_LINK,
            parse_mode="Markdown",
        )
        return

    # Handle 'photo' requests
    if any(word in text for word in ["photo", "pic", "image", "selfie"]):
        if not user["is_paid"] and user["images"] >= 2:
            await update.message.reply_text(
                "You’ve reached your *2 free photos* limit 💔\nUnlock 8 daily photos for ₹119 👉 " + PAYMENT_LINK,
                parse_mode="Markdown",
            )
            return
        elif user["is_paid"] and user["images"] >= 8:
            await update.message.reply_text("You’ve reached your 8 image limit for today 🥺")
            return

        user["images"] += 1
        await update.message.reply_chat_action("upload_photo")
        img_url = await generate_image("beautiful Indian girlfriend selfie, smiling, romantic mood, cinematic lighting")
        if img_url:
            await update.message.reply_photo(photo=img_url, caption="Here’s a pic just for you 💕")
        else:
            await update.message.reply_text("Oops! Couldn’t create a photo right now 😢")
        return

    # Message limit check
    if not user["is_paid"] and user["messages"] >= 25:
        await update.message.reply_text(
            "You’ve used all *25 free messages*, darling 😘\nUpgrade for unlimited chats + photos 💞\n👉 " + PAYMENT_LINK,
            parse_mode="Markdown",
        )
        return

    user["messages"] += 1
    reply = await chat_with_ai(text)
    await update.message.reply_text(reply)

# ----------------------------
# Flask Webhook for Render
# ----------------------------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.create_task(application.process_update(update))
    return "ok"

@app.route("/")
def home():
    return "💖 FriendifyAI Bot is Live on Render!"

# ----------------------------
# Telegram App Setup
# ----------------------------
application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ----------------------------
# Run on Render
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
