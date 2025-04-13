from db import functions as db
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import keyboards

# Handler for /start command
async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):


    telegram_id = update.effective_user.id
    user_data = db.get_user_data(telegram_id)
    if user_data:
        name = user_data['name']
    else:
        name = 'stranger'
    
    await update.message.reply_text(
        f"Hello, {name}. Please choose an option from the menu below:",
        reply_markup=InlineKeyboardMarkup(keyboards.get_main_menu_keyboard())
    )
