from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
import keyboards 
import db.functions as db

# This will be triggered when the user starts the bot
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    first_name = update.effective_user.first_name or "пользователь"

    user_data = db.get_user_data(telegram_id)

    if not user_data:
        db.create_user_if_not_exists(telegram_id)
        db.update_user_name(telegram_id, first_name)
        name_to_display = first_name
    else:
        name_to_display = user_data['name']

    await update.message.reply_text(
        f"Привет, {name_to_display}! Добро пожаловать в нашего бота. Начни с нажатия на кнопку ниже 👇",
        reply_markup=keyboards.get_start_keyboard(),
    )
