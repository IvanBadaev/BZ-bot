from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from db import functions as db
import handlers.utilities.cancel as cancel_utils
import keyboards

INPUT_NAME = range(1)

# Callback triggered when user presses the "Set Name" button
async def handle_setname_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("📝 Пожалуйста, введите ваше имя:", reply_markup=keyboards.get_cancel_keyboard())
    return INPUT_NAME

# Handles the user's name input
async def handle_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    name = update.message.text.strip()

    if not name:
        await update.message.reply_text("⚠️ Имя не может быть пустым. Попробуйте снова.")
        return INPUT_NAME

    db.update_user_name(telegram_id, name)
    await update.message.reply_text(f"✅ Спасибо, {name}! Имя сохранено.")
    return ConversationHandler.END

def get_setname_conversation_handler(command):
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_setname_callback, pattern=f"^{command}$")],
        states={
            INPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name_input)],
        },
        fallbacks=cancel_utils.get_fallbacks(),
    )

