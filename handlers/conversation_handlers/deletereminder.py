from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from db import functions as db
import handlers.utilities.cancel as cancel_utils
import keyboards
from helpers import get_reminders_table

SELECT_REMINDER, CONFIRM_REMINDER_DELETE = range(2)


# Callback triggered when the user presses the "Delete Medicine" button
async def handle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    reminders = db.get_reminders(user_id)

    if not reminders:
        await query.message.reply_text("У вас нет активных напоминаний.")
        return ConversationHandler.END

    if len(reminders) > 24:
        table = get_reminders_table(reminders)
        await query.message.reply_text("Ваши напоминания:\n\n" + table)
    else:
        await query.message.reply_text(
            "Выберите напоминание для удаления:",
            reply_markup=keyboards.get_reminder_selection_keyboard(reminders),
        )

    return SELECT_REMINDER

async def handle_select_reminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 3)
    reminder_id = int(parts[2])
    display_name = parts[3].replace("~", " ")

    await query.message.reply_text(
        f"Удалить напоминание: {display_name}?",
        reply_markup=keyboards.get_delete_confirmation_keyboard(reminder_id)
    )
    return CONFIRM_REMINDER_DELETE

async def handle_confirm_reminder_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reminder_id = int(query.data.split("_")[2])

    response = db.delete_reminder(reminder_id)

    print(f"Deleting reminder with ID: {reminder_id}")

    await query.message.reply_text(response, reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END


def get_deletereminder_conversation_handler(command):
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_delete_reminder, pattern=f"^{command}$"),
            CommandHandler(command, handle_delete_reminder),
        ],
        states={
            SELECT_REMINDER: [
                CallbackQueryHandler(handle_select_reminder_callback, pattern="^delete_reminder_")
            ],
            CONFIRM_REMINDER_DELETE: [
                CallbackQueryHandler(handle_confirm_reminder_delete, pattern="^confirm_delete_")
            ],
        },
        fallbacks=cancel_utils.get_fallbacks(),
    )
