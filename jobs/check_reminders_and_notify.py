from datetime import datetime
from telegram.ext import Application
import asyncio
from db import functions as db
import keyboards

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime

async def check_reminders_and_notify(context):
    now = datetime.now()
    current_day = now.strftime("%a")  # "Mon"
    current_time = now.strftime("%H:%M")  # "09:30"

    print(f"Checking reminders for {current_day} at {current_time}")
    reminders = db.get_reminders_by_day_and_time(current_day, current_time)


    for row in reminders:
        telegram_id = row["telegram_id"] 
        medicine_name = row["medicine_name"] 
        dose = row["dose"]
        reminder_id = row["reminder_id"]  # Be careful: this is also 'id' — may need aliasing!
        is_one_time = row["is_one_time"]
        if is_one_time:
            isPostponed = 'True'
        else:
            isPostponed = 'False'
        message = f"⏰ Напоминание: пора принять 💊 *{medicine_name}*, доза - ({dose})"

        if (is_one_time):
            status = "отложено"

        try:
            message = await context.bot.send_message(chat_id=telegram_id, text=message, parse_mode="Markdown", reply_markup=keyboards.get_handle_notification_keyboard(reminder_id, medicine_name, dose, isPostponed))
            if is_one_time:
                db.delete_one_time_reminder_schedules_by_reminder_id(reminder_id)
                print(f"One-time reminders of {reminder_id} deleted after sending.")

            now = datetime.now().isoformat(timespec='minutes')
            db.create_reminder_message(reminder_id, message.message_id, now)
            
        except Exception as e:
            print(f"Failed to send reminder to {telegram_id}: {e}")

    if not reminders:
        print("No reminders to send at this time.")

