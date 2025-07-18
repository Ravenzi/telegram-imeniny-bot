import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import datetime

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

def load_imeniny(filename='imeniny_year.txt'):
    imeniny_by_date = {}
    imeniny_by_name = {}

    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            date_part, names_part = line.split(':', 1)
            date_part = date_part.strip()
            names = [name.strip() for name in names_part.split(',')]
            imeniny_by_date[date_part] = names
            for name in names:
                if name not in imeniny_by_name:
                    imeniny_by_name[name] = []
                imeniny_by_name[name].append(date_part)
    
    return imeniny_by_date, imeniny_by_name

imeniny_by_date, imeniny_by_name = load_imeniny()

months_ru = {
    "01": "января", "02": "февраля", "03": "марта", "04": "апреля",
    "05": "мая", "06": "июня", "07": "июля", "08": "августа",
    "09": "сентября", "10": "октября", "11": "ноября", "12": "декабря"
}

def format_date(date_str):
    day, month = date_str.split("-")
    return f"{int(day)} {months_ru[month]}"

main_keyboard = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Сегодня")],
        [KeyboardButton("Выбрать дату"), KeyboardButton("По имени")]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе узнать, у кого сегодня или в выбранную дату именины.\n"
        "Ты также можешь ввести имя и узнать все даты, когда у него именины.",
        reply_markup=main_keyboard
    )

async def today_imeniny(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.datetime.now().strftime('%d-%m')
    names = imeniny_by_date.get(today)
    if names:
        await update.message.reply_text(f"🎉 Сегодня ({today}) именины у: {', '.join(names)}")
    else:
        await update.message.reply_text("😔 На сегодня именин не найдено.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()

    if msg.lower() == "сегодня":
        await today_imeniny(update, context)
        return

    if msg.lower() == "выбрать дату":
        await update.message.reply_text("📅 Введите дату в формате ДД-ММ (например: 25-07)")
        return

    if msg.lower() == "по имени":
        await update.message.reply_text("✍️ Введите имя с заглавной буквы (например: Алексей)")
        return

    try:
        datetime.datetime.strptime(msg, '%d-%m')
        names = imeniny_by_date.get(msg)
        if names:
            await update.message.reply_text(f"🎈 Именинники на {msg}: {', '.join(names)}")
        else:
            await update.message.reply_text(f"🙁 Именинников на {msg} не найдено.")
        return
    except ValueError:
        pass

    name = msg.capitalize()
    dates = imeniny_by_name.get(name)
    if dates:
        formatted = [format_date(d) for d in dates]
        await update.message.reply_text(
            f"📅 У {name} именины в следующие дни:\n" + ', '.join(formatted)
        )
    else:
        await update.message.reply_text(f"🔍 Имя {name} не найдено в календаре именин.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("today", today_imeniny))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен...")
    app.run_polling()
