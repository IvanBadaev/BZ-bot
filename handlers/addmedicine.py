from db import functions as db

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def handle_addmedicine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    # The medicine name will be passed as the second argument (after the command)
    if context.args:
        medicine_name = " ".join(context.args)  # In case the name contains spaces
        response = db.create_medicine_if_not_exists(telegram_id, medicine_name)
        await update.message.reply_text(response)
    else:
        # If the user didn't provide a medicine name
        await update.message.reply_text("Please provide the name of the medicine. For example: /addmedicine Aspirin")

