from db import functions as db  # Assuming your db logic is modular
from helpers import format_history_entries  # The formatter from before
from telegram import Update
from telegram.ext import ContextTypes
import keyboards

async def hadnle_list_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_id = query.from_user.id

    history_entries = db.get_medicine_history_for_user(telegram_id)

    if history_entries:
        formatted_history = format_history_entries(history_entries)
        await query.message.reply_text(
            f"📜 История приёма лекарств:\n\n{formatted_history}",
            parse_mode="Markdown",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
    else:
        await query.message.reply_text(
            "📭 У вас пока нет записей в истории приёма.",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
