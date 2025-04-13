import json
from telegram import InlineKeyboardButton

def get_commands():
    with open('commands.json') as f:
        return json.load(f)

def get_main_menu_keyboard():
    commands = get_commands()
    
    return [
        [InlineKeyboardButton("💬 Set name", callback_data=commands['setname'])],
        [InlineKeyboardButton("📝 Add Medicine", callback_data=commands['addmedicine'])],
        [InlineKeyboardButton("📜 List Medicines", callback_data=commands['listmedicines'])],
        [InlineKeyboardButton("📝 Add reminder", callback_data=commands['addreminder'])],
        [InlineKeyboardButton("📜 List Reminders", callback_data=commands['listreminders'])],
    ]

def get_select_medicine_keyboard(medicines):
    return [
        [InlineKeyboardButton(medicine["name"], callback_data=f"medicine_{medicine["id"]}")]
        for medicine in medicines
    ]
