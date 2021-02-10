import os
import json
import argparse
import logging
from typing import List
import _pickle as pickle
from pathlib import Path
from functools import wraps
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from config import Config
from recipes import Recipe


def read_recipes(file_path: Path):
    with file_path.open("rb") as fin:
        return pickle.load(fin)


def read_tree(file_path: Path):
    with file_path.open() as fin:
        return json.load(fin)


# TODO make configs not global
CONFIGS = Config()
PORT = int(os.environ.get('PORT', 5000))
COCKTAILS = read_recipes(Path(CONFIGS.data["recipes"]))
TREE = read_tree(Path(CONFIGS.data["tree"]))


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
    options = TREE["0"]["options"]
    message = TREE["0"]["next_question"]
    keyboard = [[InlineKeyboardButton(TREE[o]["text"], callback_data=o)] for o in options]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(message, reply_markup=reply_markup)


@restricted
def next(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    state = query.data
    options, message = TREE[state]["options"], TREE[state]["next_question"]
    if options:
        keyboard = [[InlineKeyboardButton(TREE[o]["text"], callback_data=o)] for o in options]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(text=message,
                                 reply_markup=reply_markup,
                                 chat_id=update.effective_chat.id)
    else:
        message = format_cocktail(message)
        context.bot.send_message(text=message,
                                 parse_mode=ParseMode.HTML,
                                 chat_id=update.effective_chat.id)


def to_string(some_list: List[str]) -> str:
    return "\n".join(some_list)


def format_cocktail(title: str) -> str:
    cocktail = COCKTAILS[title]
    emoji = CONFIGS.emoji
    message = f"{emoji['cocktail']} <b>{cocktail.title}</b>\n\n" \
              f"{emoji['notes']} {to_string(cocktail.notes)}\n\n" \
              f"{emoji['ingredients']} {cocktail.amount}\n" \
              f"<i>{to_string(cocktail.ingredients)}</i>\n\n" \
              f"{emoji['instructions']} {to_string(cocktail.instructions)}"
    return message


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" caused error "%s"', update, context.error)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--webhook", action='store_true',
                        help="Launch the webhook version. Polling otherwise.")
    return parser.parse_args()


def main():
    args = get_args()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    updater = Updater(token=CONFIGS.bot["token"], use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("choose", choose))
    dispatcher.add_handler(CallbackQueryHandler(next))
    # dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_error_handler(error)

    if args.webhook:
        updater.start_webhook(listen="0.0.0.0",
                              port=int(PORT),
                              url_path=CONFIGS.bot["token"])
        updater.bot.setWebhook(CONFIGS.server["address"] + CONFIGS.bot["token"])
    else:
        updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
