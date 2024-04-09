# botgerador.py

import telegram

from telegram.ext import Updater, CommandHandler, MessageHandler, filters

from functools import wraps
from datetime import datetime, timedelta

# Telegram bot token obtained from BotFather
TOKEN = '6760890328:AAFTyhR88Uf9pePTS3qemqQYDrvnNOR_oMk'

# List of admin Telegram IDs (replace with your actual ID)
ADMIN_IDS = {"5989863155"}

# Dictionary to store user privileges and their expiration timestamps
user_privileges = {}

# Function to check if the user is an admin
def is_admin(update):
    return str(update.message.chat_id) in ADMIN_IDS

# Command to add a user as a regular user with a specified duration
def add_user(update, context):
    if is_admin(update):
        if len(context.args) != 2:
            update.message.reply_text("Usage: /adduser <user_id> <duration_in_seconds>")
            return
        user_id = str(context.args[0])
        duration = int(context.args[1])  # Duration in seconds
        expiration_time = datetime.now() + timedelta(seconds=duration)
        user_privileges[user_id] = {"type": "user", "expires": expiration_time}
        update.message.reply_text(f"User {user_id} added as a regular user for {duration} seconds.")

# Function to send a welcome message
def start(update, context):
    update.message.reply_text("Welcome to the bot! This is a welcome message.")

# Function to handle messages
def echo(update, context):
    user_id = str(update.message.chat_id)
    if user_id in user_privileges:
        privilege = user_privileges[user_id]
        if datetime.now() < privilege["expires"]:
            update.message.reply_text("You are authorized to use this bot.")
        else:
            del user_privileges[user_id]
            update.message.reply_text("Your access to this bot has expired.")
    else:
        update.message.reply_text("You are not authorized to use this bot.")

# Function to restrict access to admin commands
def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        if is_admin(update):
            return func(update, context, *args, **kwargs)
        else:
            update.message.reply_text("You are not authorized to perform this action.")
    return wrapped

def main():
    # Create the bot updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("adduser", restricted(add_user), pass_args=True))
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
