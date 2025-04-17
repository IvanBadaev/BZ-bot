from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from handlers.command_handlers.help import handle_help
from handlers.command_handlers.setname import handle_setname
from handlers.command_handlers.addmedicine import handle_addmedicine
from handlers.command_handlers.listmedicines import handle_listmedicines
from handlers.command_handlers.listreminders import handle_listreminders
from handlers.command_handlers.start import handle_start
from handlers.command_handlers.unrecognized import handle_unrecognized

from handlers.callback_handlers.listmedicines import handle_listmedicines_callback
from handlers.callback_handlers.listreminders import handle_listreminders_callback
from handlers.callback_handlers.start import handle_start_callback
from handlers.callback_handlers.menu import handle_menu_callback
from handlers.callback_handlers.list_postponed_reminders import handle_list_postponed_reminders
from handlers.callback_handlers.list_history import hadnle_list_history

from handlers.conversation_handlers.setname import get_setname_conversation_handler
from handlers.conversation_handlers.addmedicine import get_addmedicine_conversation_handler
from handlers.conversation_handlers.deletereminder import get_deletereminder_conversation_handler
from handlers.conversation_handlers.addreminder import get_addreminder_conversation_handler
from handlers.conversation_handlers.deletemedicine import get_deletemedicine_conversation_handler
from handlers.conversation_handlers.handle_notification import get_handle_notification_conversation_handler

from jobs.check_reminders_and_notify import check_reminders_and_notify
from jobs.cancel_ignored_reminders import cancel_ignored_reminders

import asyncio
import db.functions as db

import helpers

def main():
    app = ApplicationBuilder().token(helpers.get_token()).build()
    app.job_queue.run_repeating(check_reminders_and_notify, interval=60, first=5)
    app.job_queue.run_repeating(cancel_ignored_reminders, interval=60, first=5)
    commands = helpers.get_commands()

    app.add_handler(CommandHandler(commands['start'], handle_start))
    app.add_handler(CommandHandler(commands['help'], handle_help))
    app.add_handler(CommandHandler(commands['menu'], handle_help))
    app.add_handler(CommandHandler(commands['setname'], handle_setname))
    app.add_handler(CommandHandler(commands['addmedicine'], handle_addmedicine))
    app.add_handler(CommandHandler(commands['listmedicines'], handle_listmedicines))
    app.add_handler(CommandHandler(commands['listreminders'], handle_listreminders))

    app.add_handler(CallbackQueryHandler(handle_listmedicines_callback, pattern=commands['listmedicines']))
    app.add_handler(CallbackQueryHandler(handle_listreminders_callback, pattern=commands['listreminders']))
    app.add_handler(CallbackQueryHandler(handle_list_postponed_reminders, pattern='list_postponed_reminders'))
    app.add_handler(CallbackQueryHandler(handle_start_callback, pattern=commands['start']))
    app.add_handler(CallbackQueryHandler(handle_menu_callback, pattern=commands['menu']))
    app.add_handler(CallbackQueryHandler(hadnle_list_history, pattern=commands['seehistory']))

    # Conversation handlers
    app.add_handler(get_addreminder_conversation_handler(command=commands['addreminder']))
    app.add_handler(get_addmedicine_conversation_handler(command=commands['addmedicine']))
    app.add_handler(get_deletereminder_conversation_handler(command=commands['deletereminder']))
    app.add_handler(get_deletemedicine_conversation_handler(command=commands['deletemedicine']))
    app.add_handler(get_setname_conversation_handler(command=commands['setname']))
    app.add_handler(get_handle_notification_conversation_handler())

    app.add_handler(MessageHandler(filters.COMMAND, handle_unrecognized))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()


