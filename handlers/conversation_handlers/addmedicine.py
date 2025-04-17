from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from db import functions as db
import keyboards
import handlers.utilities.cancel as cancel_utils

INPUT_MEDICINE_NAME = range(1)

# Callback triggered when user presses "Add Medicine"
async def handle_addmedicine_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text(
        "💊 Пожалуйста, введите название лекарства:",
        reply_markup=keyboards.get_cancel_keyboard()
    )
    return INPUT_MEDICINE_NAME

# Handles the user's medicine name input
async def handle_medicine_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicine_name = update.message.text.strip()

    if not medicine_name:
        await update.message.reply_text("⚠️ Название лекарства не может быть пустым. Попробуйте снова.")
        return INPUT_MEDICINE_NAME

    response = db.create_medicine_if_not_exists(telegram_id, medicine_name)
    await update.message.reply_text(response, reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END

# ConversationHandler for adding medicine
def get_addmedicine_conversation_handler(command):
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_addmedicine_callback, pattern=f"^{command}$")],
        states={
            INPUT_MEDICINE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_medicine_name_input)],
        },
        fallbacks=cancel_utils.get_fallbacks()
    )
