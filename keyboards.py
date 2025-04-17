import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_commands():
    with open('commands.json') as f:
        return json.load(f)

def get_main_menu_keyboard():
    commands = get_commands()
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Ввести имя", callback_data=commands['setname'])],
        [InlineKeyboardButton("💊 Добавить лекарство", callback_data=commands['addmedicine'])],
        [InlineKeyboardButton("📦 Список лекарств", callback_data=commands['listmedicines'])],
        [InlineKeyboardButton("❌ Удалить лекарство", callback_data=commands['deletemedicine'])],
        [InlineKeyboardButton("⏰ Добавить напоминание", callback_data=commands['addreminder'])],
        [InlineKeyboardButton("📋 Список напоминаний", callback_data=commands['listreminders'])],
        [InlineKeyboardButton("⏳ Отложенные напоминания", callback_data="list_postponed_reminders")],
        [InlineKeyboardButton("❌ Удалить напоминание", callback_data=commands['deletereminder'])],
        [InlineKeyboardButton("📜 Посмотреть историю приёма", callback_data=commands['seehistory'])],
    ])

def get_select_medicine_keyboard(medicines):
    return [
        [InlineKeyboardButton(medicine["name"], callback_data=f"medicine_{medicine['id']}")]
        for medicine in medicines
    ]

def get_day_selection_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Каждый день", callback_data='days_every')],
        [InlineKeyboardButton("🏢 По будням", callback_data='days_weekdays')],
        [InlineKeyboardButton("🎈 По выходным", callback_data='days_weekends')],
        [InlineKeyboardButton("🔧 Выбрать вручную", callback_data='days_custom')]
    ])

DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
DAY_CODES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def get_custom_day_keyboard(selected_days):
    keyboard = []
    for day_code, day_label in zip(DAY_CODES, DAYS):
        selected = f"✅ {day_label}" if day_code in selected_days else f"⬜ {day_label}"
        keyboard.append([InlineKeyboardButton(selected, callback_data=f"toggle_{day_code}")])

    keyboard.append([InlineKeyboardButton("✅ Готово", callback_data="days_done")])
    return InlineKeyboardMarkup(keyboard)

def get_cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ])

def get_cancel_button(text="❌ Отмена"):
    return InlineKeyboardButton(text, callback_data="cancel")

def get_medicine_selection_keyboard(medicines):
    if len(medicines) <= 24:
        keyboard = [
            [InlineKeyboardButton(medicine['name'], callback_data=f"delete_medicine_{medicine['id']}_{medicine['name']}")]
            for medicine in medicines
        ]
        keyboard.append([get_cancel_button()])
        return InlineKeyboardMarkup(keyboard)
    else:
        return False
    
def get_delete_confirmation_keyboard(item_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да", callback_data=f"confirm_delete_{item_id}")],
        [get_cancel_button("❌ Нет")]
    ])

def get_start_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛠️ Start", callback_data="menu")],
    ])

def get_reminder_selection_keyboard(reminders):
    buttons = []
    for r in reminders:
        id, time, label, dose, medicine = r
        label_str = f" ({label})" if label else ""
        display = f"{medicine} – {time}{label_str}"
        callback_data = f"delete_reminder_{id}_{display.replace(' ', '~')}"
        buttons.append([InlineKeyboardButton(display, callback_data=callback_data)])
    buttons.append([get_cancel_button()])
    return InlineKeyboardMarkup(buttons)

def get_handle_notification_keyboard(reminder_id, medicine_name, dose, isPostponed='False'):     
    keyboard = [
        [InlineKeyboardButton("Я принял", callback_data=f"done_{reminder_id}_{medicine_name}_{dose}_{isPostponed}")],
        [InlineKeyboardButton("Отложить приём", callback_data=f"postpone_{reminder_id}")],
        [InlineKeyboardButton("Сегодня не смогу принять", callback_data=f"cancel_{reminder_id}_{medicine_name}_{dose}")],
        [InlineKeyboardButton("Удалить напоминание", callback_data=f"delete_{reminder_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_postpone_keyboard(reminder_id):
    keyboard = [
        [InlineKeyboardButton("Отложить на 15 минут", callback_data=f"postpone_15_{reminder_id}")],
        [InlineKeyboardButton("Отложить на 30 минут", callback_data=f"postpone_30_{reminder_id}")],
        [InlineKeyboardButton("Отложить на 1 час", callback_data=f"postpone_60_{reminder_id}")],
        [InlineKeyboardButton("Отложить на 2 часа", callback_data=f"postpone_120_{reminder_id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_delete_reminder_confirmation_keyboard(reminder_id: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да", callback_data=f"confirm_delete_{reminder_id}")],
        [InlineKeyboardButton("❌ Нет", callback_data=f"cancel_delete_{reminder_id}")]
    ])