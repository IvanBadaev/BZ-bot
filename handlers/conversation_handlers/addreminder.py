
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from db import functions as db
from helpers import is_valid_time_format
import handlers.utilities.cancel as cancel_utils
import keyboards

SELECT_MEDICINE, INPUT_DAYS, SELECTING_CUSTOM_DAYS, INPUT_TIME, INPUT_DOSE = range(5)

async def handle_addreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicines = db.get_medicines(telegram_id)

    if not medicines:
        await update.message.reply_text("Вы пока не добавили лекарства. Нажмите /addmedicine.")
        return ConversationHandler.END

    keyboard = keyboards.get_select_medicine_keyboard(medicines)
    await update.message.reply_text("Пожалуйста выберите лекарство:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_MEDICINE

async def handle_addreminder_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    query = update.callback_query
    medicines = db.get_medicines(telegram_id)

    if not medicines:
        await query.message.reply_text("Вы пока не добавили лекарства. Нажмите /addmedicine.")
        return ConversationHandler.END

    keyboard = keyboards.get_select_medicine_keyboard(medicines)
    await query.message.reply_text("Пожалуйста выберите лекарство:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_MEDICINE


async def handle_medicine_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    medicine_id = int(query.data.split("_")[1])
    context.user_data['selected_medicine'] = medicine_id

    # Prompt user for days selection and show the day keyboard
    await query.message.reply_text(
        "Вы выбрали лекарство. В какие дни вы хотели бы получать напоминания?",
        reply_markup=keyboards.get_day_selection_keyboard()  # Send the days keyboard here
    )
    return INPUT_DAYS

async def handle_day_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_option = query.data  # like 'days_every', 'days_weekdays' etc.

    if selected_option == 'days_every':
        context.user_data['selected_days'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    elif selected_option == 'days_weekdays':
        context.user_data['selected_days'] = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    elif selected_option == 'days_weekends':
        context.user_data['selected_days'] = ['Sat', 'Sun']
    elif selected_option == 'days_custom':
        # Switch to a custom day selection handler
        await query.edit_message_text("Пожалуйста выберите конкретные дни:")
        return await handle_custom_day_selection_start(update, context)

    await query.edit_message_text("✅ Дни выбраны. Теперь выберите время (например 08:00, 13:30):")
    return INPUT_TIME

async def handle_custom_day_selection_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['selected_days'] = []
    keyboard = keyboards.get_custom_day_keyboard(context.user_data['selected_days'])

    query = update.callback_query
    await query.edit_message_text("📆 Выберите дни, в которые вы хотели бы получать напоминания:", reply_markup=keyboard)

    return SELECTING_CUSTOM_DAYS

async def handle_custom_day_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_days = context.user_data.get('selected_days', [])

    day = query.data.split("_")[1]

    if day in selected_days:
        selected_days.remove(day)
    else:
        selected_days.append(day)

    context.user_data['selected_days'] = selected_days
    keyboard = keyboards.get_custom_day_keyboard(selected_days)

    await query.edit_message_text("📆 Выберите дни, в которые вы хотели бы получать напоминания:", reply_markup=keyboard)
    return SELECTING_CUSTOM_DAYS

async def handle_custom_day_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    selected_days = context.user_data.get('selected_days', [])
    if not selected_days:
        await query.edit_message_text("⚠️ Вы не выбрали дни. Пожалуйста, выберите хотя бы один.")
        return SELECTING_CUSTOM_DAYS

    await query.edit_message_text(f"✅ Выбранные дни: {', '.join(selected_days)}\nТеперь введите время (например 08:00, 18:00):")
    return INPUT_TIME

async def handle_reminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time = update.message.text

    if not is_valid_time_format(time):
        await update.message.reply_text("⛔ Неверный формат. Пожулайста, введите в формате ЧЧ:ММ.")
        return INPUT_TIME

    context.user_data['reminder_time'] = time
    await update.message.reply_text("Отлично! Теперь введите дозу (например 2 таблетки, 5мл., etc.):")
    return INPUT_DOSE


async def handle_reminder_dose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicine_id = context.user_data.get('selected_medicine')
    time = context.user_data.get('reminder_time')
    days = context.user_data.get('selected_days')
    dose = update.message.text

    if not (medicine_id and time and dose):
        await update.message.reply_text("⚠️ Ошибка. Пожалуйста, попробуйте ещё раз. /addreminder.")
        return ConversationHandler.END

    response = db.create_reminder_with_schedule(telegram_id, medicine_id, days, time, dose, label=None)
    await update.message.reply_text(response, reply_markup=keyboards.get_main_menu_keyboard())

    return ConversationHandler.END

def get_addreminder_conversation_handler(*, command):
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_addreminder_callback, pattern=f'^{command}$'), CommandHandler(command, handle_addreminder)],
        states={
            SELECT_MEDICINE: [CallbackQueryHandler(handle_medicine_selection, pattern=r"^medicine_\d+$")],
            INPUT_DAYS: [CallbackQueryHandler(handle_day_selection, pattern=r"^days_")],
            SELECTING_CUSTOM_DAYS: [
                CallbackQueryHandler(handle_custom_day_toggle, pattern=r"^toggle_"),
                CallbackQueryHandler(handle_custom_day_done, pattern=r"^days_done$")
            ],
            INPUT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_time)],
            INPUT_DOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder_dose)],
        },
        fallbacks=cancel_utils.get_fallbacks(),
    )