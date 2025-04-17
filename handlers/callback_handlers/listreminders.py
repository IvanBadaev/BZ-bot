from db import functions as db
from telegram import Update
from telegram.ext import ContextTypes
import keyboards
from helpers import map_days_to_russian

async def handle_listreminders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_id = query.from_user.id

    # Fetch all reminders with schedule data for this user
    reminders = db.get_reminders_with_schedule(telegram_id)

    if reminders:
        grouped_reminders = {}

        for reminder in reminders:
            reminder_id = reminder['id']
            name = reminder['name']
            dose = reminder['dose']
            day_of_week = reminder['day_of_week']
            time = reminder['time']
            is_one_time = reminder['is_one_time']

            # Skip one-time postponed reminders
            if is_one_time:
                continue

            if reminder_id not in grouped_reminders:
                grouped_reminders[reminder_id] = {
                    'name': name,
                    'dose': dose,
                    'time': time,
                    'days': []
                }
            grouped_reminders[reminder_id]['days'].append(day_of_week)

        if grouped_reminders:
            sorted_reminders = sorted(grouped_reminders.values(), key=lambda r: r['name'].lower())

            reminder_list = "\n".join(
                [f"💊 {info['name']} ({info['dose']}) в дни: ({', '.join(map_days_to_russian(info['days']))}) в {info['time']}"
                 for info in sorted_reminders]
            )

            await query.message.reply_text(
                f"Вот ваши напоминания:\n{reminder_list}",
                reply_markup=keyboards.get_main_menu_keyboard()
            )
        else:
            await query.message.reply_text(
                "📭 У вас нет постоянных напоминаний. Только отложенные или удалённые.",
                reply_markup=keyboards.get_main_menu_keyboard()
            )

    else:
        await query.message.reply_text(
            "📭 Вы пока не добавили напоминаний.",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
