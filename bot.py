import os
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

load_dotenv()  # Load environment variables from .env
BOT_TOKEN = os.getenv('BOT_TOKEN')


from handlers.start import handle_start
from handlers.setname import handle_setname
from handlers.addmedicine import handle_addmedicine
from handlers.listmedicines import handle_listmedicines
from handlers.addreminder import get_addreminder_handler
from handlers.listreminders import handle_listreminders

from handlers.callback_handlers.addmedicine import handle_addmedicine_callback
from handlers.callback_handlers.listmedicines import handle_listmedicines_callback
from handlers.callback_handlers.listreminders import handle_listreminders_callback

def get_commands():
    with open('commands.json') as f:
        return json.load(f)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    commands = get_commands()

    app.add_handler(CommandHandler(commands['start'], handle_start))
    app.add_handler(CommandHandler(commands['setname'], handle_setname))
    app.add_handler(CommandHandler(commands['addmedicine'], handle_addmedicine))
    app.add_handler(CommandHandler(commands['listmedicines'], handle_listmedicines))
    app.add_handler(CommandHandler(commands['listreminders'], handle_listreminders))

    app.add_handler(CallbackQueryHandler(handle_setname, pattern='setname'))
    app.add_handler(CallbackQueryHandler(handle_addmedicine_callback, pattern='addmedicine'))
    app.add_handler(CallbackQueryHandler(handle_listmedicines_callback, pattern='listmedicines'))
    app.add_handler(CallbackQueryHandler(handle_listreminders_callback, pattern='listreminders'))

    # Conversation handlers
    app.add_handler(get_addreminder_handler())

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()


