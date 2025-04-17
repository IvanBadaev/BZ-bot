from telegram.ext import MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
import keyboards

async def handle_unrecognized(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text
    await update.message.reply_text(
        f"⚠️ Извините, я не распознал команду '{command}'. Пожалуйста, используйте команду из меню или введите /help для списка команд.",
        reply_markup=keyboards.get_main_menu_keyboard(),
    )
