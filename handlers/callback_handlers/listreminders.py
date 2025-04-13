from db import functions as db
from telegram import Update
from telegram.ext import ContextTypes

async def handle_listreminders_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Access the callback query
    query = update.callback_query
    telegram_id = query.from_user.id  # Get the user's ID from the callback query
    
    # Fetch reminders from the database
    reminders = db.get_reminders(telegram_id)
    
    print('getting reminders')
    for reminder in reminders:
        print(dict(reminder))

    if reminders:
        # Format each reminder: e.g., "💊 Aspirin (2 tablets) at 08:00 AM"
        reminder_list = "\n".join(
            [f"💊 {reminder['name']} ({reminder['dose']}) at {reminder['time']}" for reminder in reminders]
        )
        await query.message.reply_text(f"Here are your reminders:\n{reminder_list}")
    else:
        await query.message.reply_text("📭 You haven't added any reminders yet.")
