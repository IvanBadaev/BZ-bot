from db import functions as db
from telegram import Update
from telegram.ext import ContextTypes

async def handle_listmedicines_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Access the callback query
    query = update.callback_query
    telegram_id = query.from_user.id  # Get the user's ID from the callback query

    # Fetch medicines from the database
    medicines = db.get_medicines(telegram_id)
    
    if medicines:
        # Format the list of medicines into a string
        medicine_list = "\n".join([medicine["name"] for medicine in medicines])
        await query.message.reply_text(f"Here are the medicines you've added:\n{medicine_list}")
    else:
        # If the user has no medicines
        await query.message.reply_text("You haven't added any medicines yet.")
