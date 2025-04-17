from db import functions as db

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import keyboards

async def handle_listmedicines(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    medicines = db.get_medicines(telegram_id)
    
    if medicines:
        # Format the list of medicines into a string
        medicine_list = "\n".join([medicine["name"] for medicine in medicines])
        await update.message.reply_text(f"Вот лекарства, которые вы добавили:\n{medicine_list}", reply_markup=keyboards.get_main_menu_keyboard())
    else:
        # If the user has no medicines
        await update.message.reply_text("Вы пока не добавили лекарств.", reply_markup=keyboards.get_main_menu_keyboard())
