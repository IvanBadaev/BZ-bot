from db import functions as db

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import keyboards

async def handle_setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❗Пожалуйста введите ваше имя. Формат команды: /setname Ваше имя")
        return

    name = ' '.join(context.args)

    db.update_user_name(telegram_id, name)

    await update.message.reply_text(f"✅ Понял, {name}! Ваше имя сохранено.", reply_markup=keyboards.get_main_menu_keyboard())