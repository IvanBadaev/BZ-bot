from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    filters,
)
from db import functions as db
import handlers.utilities.cancel as cancel_utils
import keyboards

SELECT_MEDICINE, CONFIRM_DELETE = range(2)


# Callback triggered when the user presses the "Delete Medicine" button
async def handle_delete_medicine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    medicines = db.get_medicines(user_id)

    # Send either a keyboard or table based on the number of medicines
    if len(medicines) > 24:
        table = "\n".join(
            [f"{idx + 1}. {medicine[1]}" for idx, medicine in enumerate(medicines)]
        )
        await query.message.reply_text("Выберите одно из списка:\n\n" + table)
    else:
        await query.message.reply_text(
            "Выберите лекарство для удаления:",
            reply_markup=keyboards.get_medicine_selection_keyboard(medicines),
        )
    return SELECT_MEDICINE


# Handle the user selecting a medicine to delete (either from keyboard or typed)


async def handle_select_medicine_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    query = update.callback_query
    medicine_id = int(query.data.split("_")[2])
    medicine_name = query.data.split("_")[3]

    await query.answer()
    await query.message.reply_text(
        f"Вы действительно хотите удалить лекарство под названием {medicine_name}?",
        reply_markup=keyboards.get_delete_confirmation_keyboard(medicine_id),
    )

    return CONFIRM_DELETE


async def handle_select_medicine_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    medicine_name = update.message.text.strip()

    medicines = db.get_medicines(user_id)

    medicine = next(
        (m for m in medicines if m[1].lower() == medicine_name.lower()), None
    )

    if medicine:
        medicine_id = medicine[0]
        await update.message.reply_text(
            f"Вы действительно хотите удалить лекарство под названием {medicine_name}?",
            reply_markup=keyboards.get_delete_confirmation_keyboard(medicine_id),
        )
    else:
        await update.message.reply_text(
            "⚠️ Лекарство не найдено. Пожалуйста, выберите правильное имя."
        )

    return CONFIRM_DELETE

async def handle_confirm_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    medicine_id = int(query.data.split("_")[2])

    print(f"Deleting medicine with ID: {medicine_id}")

    response = db.delete_medicine(user_id, medicine_id)

    await query.message.reply_text(response, reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END


def get_deletemedicine_conversation_handler(command):
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_delete_medicine, pattern=f"^{command}$"),
            CommandHandler(command, handle_delete_medicine),
        ],
        states={
            SELECT_MEDICINE: [
                CallbackQueryHandler(
                    handle_select_medicine_callback, pattern="^delete_medicine_"
                ),
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_select_medicine_message
                ),
            ],
            CONFIRM_DELETE: [
                CallbackQueryHandler(
                    handle_confirm_delete, pattern="^confirm_delete_"
                ),
            ],
        },
        fallbacks=cancel_utils.get_fallbacks(),
    )
