import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

def is_valid_time_format(time: str):
    import re
    pattern = r"^([01]?[0-9]|2[0-3]):([0-5]?[0-9])$"  # Regex for HH:MM format
    return bool(re.match(pattern, time))

def get_reminders_table(reminders):
    """
    Takes a list of reminders and formats them into a clean numbered table string.
    Each reminder is expected to be a tuple: (time, label, dose, medicine_name)
    """
    lines = []
    for idx, (time, label, dose, medicine) in enumerate(reminders, start=1):
        label_str = f" ({label})" if label else ""
        dose_str = f", {dose}" if dose else ""
        line = f"{idx}. {medicine} – {time}{label_str}{dose_str}"
        lines.append(line)
    return "\n".join(lines)

def get_commands():
    with open('commands.json') as f:
        return json.load(f)
    
def get_token():
    load_dotenv() 
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    if not BOT_TOKEN:
        raise ValueError("No token found in environment variables. Please set BOT_TOKEN in your .env file.")
    return BOT_TOKEN

def map_day_to_russian(day_abbr: str) -> str:
    day_mapping = {
        "Mon": "Понедельник",
        "Tue": "Вторник",
        "Wed": "Среда",
        "Thu": "Четверг",
        "Fri": "Пятница",
        "Sat": "Суббота",
        "Sun": "Воскресенье"
    }
    
    return day_mapping.get(day_abbr, day_abbr)  # In case of an invalid input, return the day as is.

def map_days_to_russian(days: list) -> list:
    day_mapping = {
        "Mon": "Понедельник",
        "Tue": "Вторник",
        "Wed": "Среда",
        "Thu": "Четверг",
        "Fri": "Пятница",
        "Sat": "Суббота",
        "Sun": "Воскресенье"
    }

    return [day_mapping.get(day, day) for day in days]

def format_history_entries(entries):
    if not entries:
        return "📭 История приёма пуста."

    lines = []
    for name, dose, taken_at, day, status in entries:
        date_time = datetime.fromisoformat(taken_at)
        date_str = date_time.strftime("%d %b, %a в %H:%M")

        # Format the entry based on its status
        if status == "done":
            status_emoji = "✅"
            status_text = "Принято"
        elif status == "done_postponed":
            status_emoji = "⏳"
            status_text = "Отложено и принято"
        elif status == "cancelled":
            status_emoji = "❌"
            status_text = "Отменено"
        else:
            status_emoji = "❓"
            status_text = "Неизвестный статус"

        # Create the line for the history entry
        lines.append(f"{status_emoji} {date_str} — 💊 *{name}* ({dose}) — {status_text}")

    return "\n".join(lines)
