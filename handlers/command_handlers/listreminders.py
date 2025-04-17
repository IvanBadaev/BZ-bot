from db import functions as db
from telegram import Update
from telegram.ext import ContextTypes
from helpers import map_days_to_russian
import keyboards

async def handle_listreminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    reminders = db.get_reminders(telegram_id)

    for reminder in reminders:
        print(dict(reminder))  

    if reminders:
        # Group reminders by reminder_id
        grouped_reminders = {}
        for reminder in reminders:
            reminder_id = reminder['id']
            name = reminder['name']
            dose = reminder['dose']
            day_of_week = reminder['day_of_week']
            time = reminder['time']
            is_one_time = reminder['is_one_time']
            
            if reminder_id not in grouped_reminders:
                grouped_reminders[reminder_id] = {
                    'name': name,
                    'dose': dose,
                    'time': time,
                    'days': []
                }
            grouped_reminders[reminder_id]['days'].append(day_of_week)
        
        sorted_reminders = sorted(grouped_reminders.values(), key=lambda r: r['name'].lower())

        reminder_list = "\n".join(
            [f"💊 {info['name']} ({info['dose']}) в дни: ({', '.join(map_days_to_russian(info['days']))}) в {info['time']}"
             for info in sorted_reminders]
        )
        
        await update.message.reply_text(f"Вот ваши напоминания:\n{reminder_list}", reply_markup=keyboards.get_main_menu_keyboard())
    else:
        await update.message.reply_text("📭 Вы пока не добавили напоминаний.", reply_markup=keyboards.get_main_menu_keyboard())
