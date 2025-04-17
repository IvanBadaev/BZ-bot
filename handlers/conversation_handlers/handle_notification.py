from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import timedelta
import keyboards
from datetime import datetime, timedelta
from db import functions as db

# Define conversation states
POSTPONE, DELETE, CANCEL = range(3)

# Postpone reminder handler
async def postpone_reminder(update, context):
    query = update.callback_query
    reminder_id = int(query.data.split('_')[1])

    await query.message.edit_text("⏳ Пожалуйста выберите, на какое время вы хотели бы отложить приём лекарства:", reply_markup=keyboards.get_postpone_keyboard(reminder_id))
    return POSTPONE

# Handle postponing the reminder by a given duration
async def handle_postpone_duration(update, context):
    query = update.callback_query
    
    minutes = int(query.data.split('_')[1])
    reminder_id = int(query.data.split('_')[2])

    
    now = datetime.now()
    current_day = now.strftime("%a") 
    current_time = now.strftime("%H:%M")  
    new_time = (now + timedelta(minutes=minutes)).strftime("%H:%M")

    db.create_reminder_schedule(reminder_id, current_day, new_time, is_one_time=True)

    await query.message.edit_text(f"⏳ Напоминание отложено на {minutes} минут. Новое время: {new_time}.")

    return ConversationHandler.END

async def handle_cancel_callback(update, context):
    query = update.callback_query

    reminder_id = int(query.data.split('_')[1])
    medicine_name = query.data.split('_')[2]
    dose = query.data.split('_')[3]
    status = 'cancelled'

    db.create_medical_history_entry_now(update.effective_user.id, medicine_name, dose, status, reminder_id)

    await query.message.edit_text("😔 Очень жаль! Постарайтесь принимать лекарства по графику и берегите своё здоровье.")
    return ConversationHandler.END

# Handle deletion confirmation
async def delete_reminder(update, context):
    query = update.callback_query
    reminder_id = int(query.data.split('_')[1])

    await query.message.edit_text("❌ Вы точно хотите удалить это напоминание? Все связанные с ним уведомления будут отменены.", reply_markup=keyboards.get_delete_confirmation_keyboard(reminder_id))
    return DELETE

# Handle delete confirmation
async def confirm_delete(update, context):
    query = update.callback_query
    reminder_id = int(query.data.split('_')[2])

    db.delete_reminder(reminder_id) 
    await query.message.edit_text("❌ Напоминание было удалено.")

    return ConversationHandler.END

# Handle cancellation of the conversation
async def cancel_delete(update, context):
    query = update.callback_query
    reminder_id = int(query.data.split('_')[1])

    await return_to_reminder_dialog(update, context, reminder_id)

    return POSTPONE  

# A function to return to the reminder dialog
async def return_to_reminder_dialog(update, context, reminder_id):
    query = update.callback_query
    await query.message.edit_text("📅 Вы вернулись к напоминанию. Выберите действие:", reply_markup=keyboards.get_handle_notification_keyboard(reminder_id))

# Handle the "done" button (user confirms they took their medicine)
async def handle_done_callback(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    reminder_id = int(query.data.split('_')[1])
    medicine_name = query.data.split('_')[2]
    dose = query.data.split('_')[3]
    isPostponed = query.data.split('_')[4]

    if (isPostponed == 'True'):
        status = "done_postponed"
    else:
        status = "done"

    db.create_medical_history_entry_now(user_id, medicine_name, dose, status, reminder_id)

    praise_messages = [
        "🌟 Отлично! Ты позаботился о себе 💚",
        "💪 Молодец! Один шаг ближе к здоровью!",
        "🎉 Прекрасно! Лекарство принято, ты — герой дня!",
        "👏 Хорошая работа! Продолжай в том же духе!",
        "🧘 Ты на правильном пути, гордимся тобой!"
    ]

    import random
    message = random.choice(praise_messages)

    await query.message.edit_text(message)

    return ConversationHandler.END


# Create the Conversation Handler
def get_handle_notification_conversation_handler():
    return ConversationHandler(
        entry_points=[CallbackQueryHandler(postpone_reminder, pattern='postpone_*'),
                    CallbackQueryHandler(delete_reminder, pattern='delete_*'),
                    CallbackQueryHandler(handle_done_callback, pattern='done_*'),
                    CallbackQueryHandler(handle_cancel_callback, pattern='cancel_*')],
        states={
            POSTPONE: [CallbackQueryHandler(handle_postpone_duration, pattern=r'postpone_\d+')],
            DELETE: [CallbackQueryHandler(confirm_delete, pattern=r'confirm_delete_*')],
        },
        fallbacks=[CallbackQueryHandler(cancel_delete, pattern=r'cancel_*')]
    )
