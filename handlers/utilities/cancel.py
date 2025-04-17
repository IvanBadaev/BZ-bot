from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
import keyboards

async def handle_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text("🚫 Действие отменено.", reply_markup=keyboards.get_main_menu_keyboard())
    else:
        await update.message.reply_text("🚫 Действие отменено.", reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END  

def get_fallbacks():
    return [
            CallbackQueryHandler(handle_cancel, pattern="^cancel$"), 
            MessageHandler(filters.COMMAND, handle_cancel),
        ]