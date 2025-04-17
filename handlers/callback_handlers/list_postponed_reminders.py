from db import functions as db
from telegram import Update
from telegram.ext import ContextTypes
import keyboards
from helpers import map_days_to_russian

async def handle_list_postponed_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_id = query.from_user.id
    
    reminders = db.get_postponed_reminders(telegram_id)
    
    if reminders:
        grouped = {}
        for reminder_id, name, dose, day_of_week, time in reminders:
            if reminder_id not in grouped:
                grouped[reminder_id] = {
                    "name": name,
                    "dose": dose,
                    "times": []
                }
            grouped[reminder_id]["times"].append((day_of_week, time))
        
        result = "\n".join([
            f"💤 {info['name']} ({info['dose']}) — отложено на: {', '.join([f'{map_days_to_russian([day])} в {time}' for day, time in info['times']])}"
            for info in grouped.values()
        ])
        
        await query.message.reply_text(f"Вот ваши отложенные напоминания:\n{result}", reply_markup=keyboards.get_main_menu_keyboard())
    else:
        await query.message.reply_text("📭 У вас нет отложенных напоминаний.", reply_markup=keyboards.get_main_menu_keyboard())
