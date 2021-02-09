import os
import json
import logging
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from config import Config


PORT = int(os.environ.get('PORT', 5000))
CONFIGS = Config()
# TODO make configs not global
with open("data.json") as fin:
    DATA = json.load(fin)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in CONFIGS.bot["allowed"]:
            logging.info(f"Unauthorized access denied for {user_id}.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped
# TODO add message when access is restricted


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hi! This bot can guide you through choosing a perfect cocktail. "
                                  "If you want to test this bot, contact @no_sweeterr. \n\n"
                                  "/start - Description and list of commands.\n"
                                  "/choose - Start choosing a cocktail.")


@restricted
def choose(update: Update, context: CallbackContext) -> None:
    state = 0
    options = DATA[str(state)]["options"]
    while options:
        message = DATA[str(state)]["text"]
        keyboard = [[InlineKeyboardButton(o, callback_data=options[o]) for o in options]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(message, reply_markup=reply_markup)
        state = options[]


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater = Updater(token=CONFIGS.bot["token"], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("choose", choose))
    # dispatcher.add_error_handler(error)
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=int(PORT),
    #                       url_path=CONFIGS.bot["token"])
    # updater.bot.setWebhook(CONFIGS.server["address"] + CONFIGS.bot["token"])
    # updater.idle()

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    # updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

if __name__ == "__main__":
    main()
