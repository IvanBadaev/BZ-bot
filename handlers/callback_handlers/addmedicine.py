from db import functions as db

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def handle_addmedicine_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.effective_user.id
    query = update.callback_query

    if query:
            await query.answer()  # Acknowledge the callback query (important!)

            # Check if context.args has data (though this is more applicable for command handlers, not callbacks)
            if context.args:
                medicine_name = " ".join(context.args)  # In case the name contains spaces
                response = db.create_medicine_if_not_exists(telegram_id, medicine_name)
                await query.message.reply_text(response)  # Update the message with the response
            else:
                await query.message.reply_text("Please provide the name of the medicine. For example: /addmedicine Aspirin")

