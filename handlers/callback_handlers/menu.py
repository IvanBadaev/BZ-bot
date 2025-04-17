from db import functions as db
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import keyboards

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    telegram_id = query.from_user.id
    first_name = query.from_user.first_name or "пользователь"

    user_data = db.get_user_data(telegram_id)

    if not user_data:
        db.create_user_if_not_exists(telegram_id)
        db.update_user_name(telegram_id, first_name)

    await query.answer()
    await query.message.reply_text(
        f"Вот доступные действия:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )
