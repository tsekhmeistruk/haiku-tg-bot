# Import necessary libraries
import os
import openai
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load environment variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROMPT = os.getenv("PROMPT")  # Load the prompt from GitHub Secrets

# Set OpenAI API key
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    raise ValueError("Error: OPENAI_API_KEY environment variable is not set.")

# Function to generate a haiku using OpenAI GPT-4
def generate_haiku():
    # Use the prompt from the environment variable
    if not PROMPT:
        raise ValueError("Error: PROMPT environment variable is not set.")
    
    prompt = PROMPT + "\n\n"

    # Read examples from haiku_examples.txt
    try:
        with open("haiku_examples.txt", "r", encoding="utf-8") as file:  # Ensure UTF-8 encoding for proper text handling
            examples = file.read()
            prompt += "Примеры:\n" + examples + "\n\n"
    except FileNotFoundError:
        return "Error: haiku_examples.txt file not found."

    # Generate haiku using OpenAI
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use GPT-4 if available
            prompt=prompt,
            max_tokens=50,
            temperature=0.7
        )
        haiku = response.choices[0].text.strip()
        return haiku
    except Exception as e:
        return f"An error occurred while generating the haiku: {e}"

# Command handler for /хоку
def haiku_command(update: Update, context: CallbackContext):
    haiku = generate_haiku()
    update.message.reply_text(haiku)

# Function to handle the /help command
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "Welcome to the Samurai Haiku Bot!\n\n"
        "Commands:\n"
        "/хоку - Generate a melancholic, reflective haiku from a samurai's perspective.\n"
        "/help - Show this help message.\n"
        "/ping - Check if the bot is alive.\n\n"
        "Enjoy the wisdom of the samurai!"
    )
    update.message.reply_text(help_text)

# Function to handle the /ping command
def ping_command(update: Update, context: CallbackContext):
    update.message.reply_text("Pong! The bot is alive.")

# Main function to set up the bot
def main():
    # Check if TELEGRAM_TOKEN is set
    if not TELEGRAM_TOKEN:
        raise ValueError("Error: TELEGRAM_TOKEN environment variable is not set.")

    # Initialize the bot and updater
    bot = Bot(token=TELEGRAM_TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("хоку", haiku_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ping", ping_command))

    # Start the bot
    updater.start_polling()
    updater.idle()

# Entry point
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")