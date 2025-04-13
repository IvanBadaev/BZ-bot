from db import functions as db

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def handle_setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text("❗Please provide your name. Usage: /setname YourName")
        return

    name = ' '.join(context.args)

    db.update_user_name(telegram_id, name)

    await update.message.reply_text(f"✅ Got it, {name}! Your name has been saved.")