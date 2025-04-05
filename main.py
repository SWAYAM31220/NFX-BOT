import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
from quart import Quart, request

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Render public URL

# States
CHOOSE_CATEGORY, TYPING_REQUEST = range(2)
user_category = {}

# Initialize app and bot
app = Quart(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [['Movies', 'Modded APKs', 'Courses']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Welcome! Please choose a category to request:", reply_markup=reply_markup)
    return CHOOSE_CATEGORY

async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    user_category[update.message.from_user.id] = category
    await update.message.reply_text(f"Type your request for {category}.")
    return TYPING_REQUEST

async def receive_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    category = user_category.get(user.id, "Unknown")
    request_text = update.message.text

    message = (
        f"New Request:\n"
        f"From: @{user.username or 'NoUsername'}\n"
        f"Category: {category}\n"
        f"Request: {request_text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    keyboard = [['Movies', 'Modded APKs', 'Courses']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Request sent! Want to make another one?", reply_markup=reply_markup)
    return CHOOSE_CATEGORY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# Conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSE_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen)],
        TYPING_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_request)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

telegram_app.add_handler(conv_handler)

# Quart webhook endpoint
@app.post("/webhook")
async def webhook():
    update = Update.de_json(await request.json, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

# Set webhook on startup
@app.before_serving
async def init():
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")

# Run the app
if __name__ == "__main__":
    app.run(port=10000)
