from datetime import datetime, timedelta
from db import functions as db
from telegram import Bot
from telegram.ext import ContextTypes

# Function to check for expired reminders and cancel them
async def cancel_ignored_reminders(context: ContextTypes.DEFAULT_TYPE):
    time_limit = (datetime.now() - timedelta(minutes=2)).isoformat(timespec='minutes')
    reminders_to_cancel = db.get_overdue_reminders(time_limit) 

    for reminder in reminders_to_cancel:
        message_id = reminder['message_id']
        reminder_id = reminder['reminder_id']
        user_id = reminder['user_id']
        medicine_name = reminder['name']
        dose = reminder['dose']
        sent_at = reminder['sent_at']

        db.create_medical_history_entry_now(user_id, medicine_name, dose, 'cancelled', reminder_id, sent_at)

        try:
            db.delete_reminder_message(message_id) 
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=(
                    f"❌ К сожалению, вы пропустили приём 💊 *{medicine_name}* ({dose}).\n"
                    "Пожалуйста, постарайтесь принимать лекарства вовремя для поддержания здоровья!"
                ),
                parse_mode='Markdown'
            )       
        except Exception as e:
            print(f"Error deleting message {message_id}: {e}")

        print(f"Reminder {reminder_id} cancelled due to inactivity")