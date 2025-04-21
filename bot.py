import os
import random
from dotenv import load_dotenv
from openai import OpenAI
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Завантаження конфігурації ---
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise EnvironmentError("TELEGRAM_TOKEN не встановлений.")
if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY не встановлений.")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- Логіка генерації ---
def read_haiku_examples() -> str:
    try:
        with open("haiku_examples.txt", "r", encoding="utf-8") as file:
            examples = file.read().strip()
            return f"\n\nПриклади хайку:\n{examples}" if examples else ""
    except Exception as e:
        return f"\n\n# (Не вдалося завантажити приклади хайку: {e})"

def ask_openai(prompt: str, max_tokens: int = 200, temperature: float = 0.6) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Помилка при генерації: {e}"

def generate_haiku() -> str:
    examples = read_haiku_examples()
    prompt = f"Склади хайку за прикладом:{examples}. Передає настрій самурая що починає свій ранок зі склянкою саке."
    return ask_openai(prompt)

def generate_mood() -> str:
    prompt = (
        "Скажи коротку фразу (одне коротке речення), "
        "яка передає настрій самурая. Це може бути тонкий жарт, дивна думка, "
        "глибокий сум або тверезе усвідомлення після веселої ночі. Все в одному реченні."
    )
    return ask_openai(prompt)

def generate_battle_haiku(name1: str, name2: str) -> tuple[str, str]:
    prompt_template = (
        "Склади коротке хайку від імені самурая {name}, "
        "який бере участь у дуелі з самураєм {opponent}. "
        "Хайку має бути зухвалим, іронічним, з претензією на перемогу, але батл закінчується сумісним розпиттям алкогольних напоїв. "
        "Може зачіпати суперника, але без прямих образ. "
        "Ім’я {name} та ім’я {opponent} мають бути у тексті."
    )

    haiku1 = ask_openai(prompt_template.format(name=name1, opponent=name2))
    haiku2 = ask_openai(prompt_template.format(name=name2, opponent=name1))
    return haiku1, haiku2

def generate_les_podervianskyi_haiku() -> str:
    try:
        with open("les_podervianskyi_quotes.txt", "r", encoding="utf-8") as file:
            quotes = [line.strip() for line in file.read().split("\n\n") if line.strip()]
        return random.choice(quotes)
    except Exception as e:
        return f"Не вдалося завантажити вислови Леся: {e}"

# --- Обробники команд ---
async def haiku_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    haiku = generate_haiku()
    await update.message.reply_text(haiku)

async def mood_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood = generate_mood()
    await update.message.reply_text(mood)

async def battle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Будь ласка, вкажи імена двох самураїв: /battle Ім’я1 Ім’я2")
        return

    name1, name2 = args[0].capitalize(), args[1].capitalize()
    haiku1, haiku2 = generate_battle_haiku(name1, name2)

    text = (
        f"⚔️ *Дуель самураїв!*\n\n"
        f"👤 *{name1}*:\n_{haiku1}_\n\n"
        f"👤 *{name2}*:\n_{haiku2}_"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "👘 *Samurai Haiku Bot*\n\n"
        "📝 *Команди:*\n"
        "/haiku — створити хайку\n"
        "/mood — настрій самурая\n"
        "/battle Ім’я1 Ім’я2 — дуель між двома самураями\n"
        "/ping — перевірка роботи\n"
        "_Слова закінчуються, але хайку — ніколи_"
    )

    keyboard = [
        [InlineKeyboardButton("🍾 Хайку", callback_data="haiku")],
        [InlineKeyboardButton("🚬 Настрій", callback_data="mood")],
        [InlineKeyboardButton("🥷 Дуель", callback_data="battle")],
        [InlineKeyboardButton("🩸 Лесь П.", callback_data="les")]
    ]
    await update.message.reply_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "haiku":
        result = generate_haiku()
        await query.message.reply_text(result)

    elif query.data == "mood":
        result = generate_mood()
        await query.message.reply_text(result)

    elif query.data == "battle":
        context.user_data["awaiting_name1"] = True
        await query.message.reply_text("Введи ім’я першого самурая:")
    elif query.data == "les":
        result = generate_les_podervianskyi_haiku()
        await query.message.reply_text(result)

async def user_input_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    text = update.message.text.strip().capitalize()

    if user_data.get("awaiting_name1"):
        user_data["name1"] = text
        user_data["awaiting_name1"] = False
        user_data["awaiting_name2"] = True
        await update.message.reply_text("А тепер ім’я другого самурая:")

    elif user_data.get("awaiting_name2"):
        user_data["name2"] = text
        user_data["awaiting_name2"] = False

        name1 = user_data.pop("name1", "Самурай1")
        name2 = user_data.pop("name2", "Самурай2")
        haiku1, haiku2 = generate_battle_haiku(name1, name2)

        text = (
            f"⚔️ *Дуель самураїв!*\n\n"
            f"👤 *{name1}*:\n_{haiku1}_\n\n"
            f"👤 *{name2}*:\n_{haiku2}_"
        )
        await update.message.reply_text(text, parse_mode="Markdown")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Pong! Я працюю.")

# --- Точка входу ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("haiku", haiku_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("battle", battle_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), user_input_handler))

    print("🤖 Бот запущено...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"Помилка при запуску: {err}")
