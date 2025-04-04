from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


# States
WAIT_JOIN, CHOOSE_CATEGORY, TYPING_REQUEST = range(3)

# Replace with your real channel links
CHANNEL_LINKS = {
    "Movies Channel": "https://t.me/+m4n8-lusbrs4M2E1",
    "Modded APKs Channel": "https://t.me/yourapkchannel",
    "Courses Channel": "https://t.me/yourcourseschannel"
}

# Temporarily store user category selection
user_category = {}

# /start command: send welcome + ask to join channels
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton(name, url=url)] for name, url in CHANNEL_LINKS.items()
    ]
    buttons.append([InlineKeyboardButton("I've Joined All Channels", callback_data="joined")])
    reply_markup = InlineKeyboardMarkup(buttons)

    welcome_msg = (
        "Hey there! Welcome to the Request Bot.\n\n"
        "To use this bot, please join all our channels first:"
    )
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    return WAIT_JOIN

# Callback after user clicks "I've Joined"
async def joined_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [['Movies', 'Modded APKs', 'Courses']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await query.edit_message_text("Thanks for joining! What do you need help with?")
    await query.message.reply_text("Choose a category:", reply_markup=reply_markup)
    return CHOOSE_CATEGORY

# Handle category selection
async def category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    user_category[update.message.from_user.id] = category
    await update.message.reply_text(f"Great! Please type your request for {category}.")
    return TYPING_REQUEST

# Handle request input
async def receive_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    request_text = update.message.text
    category = user_category.get(user.id, "Unknown")

    message = (
        f"New Request:\n"
        f"From: @{user.username or 'NoUsername'}\n"
        f"Category: {category}\n"
        f"Request: {request_text}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=message)
    await update.message.reply_text("Your request has been sent. Thank you!")

    # Restart selection
    keyboard = [['Movies', 'Modded APKs', 'Courses']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Want to request something else? Choose a category:", reply_markup=reply_markup)
    return CHOOSE_CATEGORY

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Request cancelled.")
    return ConversationHandler.END

# Main app function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WAIT_JOIN: [CallbackQueryHandler(joined_channels, pattern='^joined$')],
            CHOOSE_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_chosen)],
            TYPING_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
