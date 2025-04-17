import helpers
from telegram import Update
from telegram.ext import ContextTypes
import keyboards

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = helpers.get_commands()
    
    command_list = "\n".join([f"/{command}: {description}" for command, description in commands.items()])
    
    await update.message.reply_text(
        f"Вот доступные действия:\n\n{command_list}",
        reply_markup=keyboards.get_main_menu_keyboard() 
    )