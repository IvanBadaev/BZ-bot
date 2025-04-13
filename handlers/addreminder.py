
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db import functions as db
from helpers import is_valid_time_format
import keyboards

SELECT_MEDICINE, INPUT_TIME, INPUT_DOSE = range(3)

async def handle_addreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicines = db.get_medicines(telegram_id)

    if not medicines:
        await update.message.reply_text("You don't have any medicines added. Please add one first with /addmedicine.")
        return ConversationHandler.END

    keyboard = keyboards.get_select_medicine_keyboard(medicines)
    await update.message.reply_text("Please select a medicine:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_MEDICINE

async def handle_addreminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    query = update.callback_query
    medicines = db.get_medicines(telegram_id)

    if not medicines:
        await query.message.reply_text("You don't have any medicines added. Please add one first with /addmedicine.")
        return ConversationHandler.END

    keyboard = keyboards.get_select_medicine_keyboard(medicines)
    await query.message.reply_text("Please select a medicine:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_MEDICINE


async def handle_medicine_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    medicine_id = int(query.data.split("_")[1])
    context.user_data['selected_medicine'] = medicine_id

    await query.message.reply_text("You selected a medicine. Now, please enter the time (HH:MM):")
    return INPUT_TIME


async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text

    if not is_valid_time_format(time):
        await update.message.reply_text("⛔ Invalid time format. Please use HH:MM.")
        return INPUT_TIME

    context.user_data['reminder_time'] = time
    await update.message.reply_text("Great! Now enter the dose (e.g. 2 tablets, 5ml, etc.):")
    return INPUT_DOSE


async def handle_reminder_dose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicine_id = context.user_data.get('selected_medicine')
    time = context.user_data.get('reminder_time')
    dose = update.message.text

    if not (medicine_id and time and dose):
        await update.message.reply_text("⚠️ Something went wrong. Please start again with /addreminder.")
        return ConversationHandler.END

    response = db.create_reminder_if_not_exists(telegram_id, medicine_id, time, dose)
    await update.message.reply_text(response)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚫 Reminder creation cancelled.")
    return ConversationHandler.END

def get_addreminder_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_addreminder_callback, pattern="addreminder"), CommandHandler("addreminder", handle_addreminder)],
        states={
            SELECT_MEDICINE: [CallbackQueryHandler(handle_medicine_selection, pattern=r"^medicine_\d+$")],
            INPUT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_time)],
            INPUT_DOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_dose)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )