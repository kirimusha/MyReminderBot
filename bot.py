import logging
import datetime
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 🔑 Твой токен от BotFather
TOKEN = "8333327080:AAEvHh6iWjg1LiSFKPsoxXMbC8k-UXOiT68"

# Смешная картинка для напоминаний
FUNNY_IMAGE = "https://disk.yandex.ru/i/OCg6p12zaV_3Lg"

# Картинки для /baby
BABY_IMAGES = [
    "https://disk.yandex.ru/i/lA_mVdPimm-F8Q",
    "https://disk.yandex.ru/i/noQR8UEWMNTRxw",
]

# ===== Команды =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in context.application.chat_data:
        context.application.chat_data[chat_id] = {"exam_date": None}
    await update.message.reply_text(
        "👋 Привет! Я бот-напоминалка.\n\n"
        "Я буду напоминать о контрольной:\n"
        "• за 3 дня\n• за 1 день\n• в день Х\n\n"
        "Команды:\n/help – список всех команд"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 Список команд:\n\n"
        "/start – включить бота\n"
        "/setdate YYYY-MM-DD – установить дату контрольной\n"
        "/when – показать дату и сколько дней осталось\n"
        "/baby – \n"
        "/help – показать список команд"
    )
    await update.message.reply_text(text)

async def set_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("❌ Используй так: /setdate YYYY-MM-DD")
        return

    try:
        exam_date = datetime.datetime.strptime(context.args[0], "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("❌ Неверный формат! Используй YYYY-MM-DD (например: 2025-09-20)")
        return

    old_date = context.chat_data.get("exam_date")

    # сохраняем в chat_data
    context.chat_data["exam_date"] = exam_date

    if old_date:
        await update.message.reply_text(
            f"🔄 Дата обновлена: была {old_date.strftime('%d.%m.%Y')}, теперь {exam_date.strftime('%d.%m.%Y')}"
        )
    else:
        await update.message.reply_text(f"✅ Контрольная назначена на {exam_date.strftime('%d.%m.%Y')}")


async def when(update: Update, context: ContextTypes.DEFAULT_TYPE):
    exam_date = context.chat_data.get("exam_date")

    if not exam_date:
        await update.message.reply_text("❌ Дата контрольной пока не установлена. Введи: /setdate YYYY-MM-DD")
        return

    days_left = (exam_date - datetime.date.today()).days
    if days_left > 0:
        await update.message.reply_text(f"📅 Контрольная назначена на {exam_date.strftime('%d.%m.%Y')}.\n"
                                        f"⏳ Осталось {days_left} дн.")
    elif days_left == 0:
        await update.message.reply_text(f"🔥 Сегодня ({exam_date.strftime('%d.%m.%Y')}) контрольная!")
    else:
        await update.message.reply_text(f"✅ Контрольная уже прошла ({exam_date.strftime('%d.%m.%Y')}).")


async def baby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img = random.choice(BABY_IMAGES)
    await update.message.reply_photo(img, caption="Вот тебе /baby")

# ===== Ежедневная проверка =====
async def daily_check(context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()

    for chat_id, data in context.application.chat_data.items():
        exam_date = data.get("exam_date")
        if not exam_date:
            continue

        days_left = (exam_date - today).days

        if days_left in [3, 1, 0]:
            if days_left == 3:
                text = "🚨 Контрольная через 3 дня! Готовься 💀📚"
            elif days_left == 1:
                text = "⚡ Завтра контрольная! Последний шанс повторить 😱📖"
            elif days_left == 0:
                text = "🔥 Сегодня контрольная! Удачи, ты справишься ✨✍️"

            await context.bot.send_photo(chat_id, FUNNY_IMAGE, caption=text)

# ===== Запуск =====
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("setdate", set_date))
    app.add_handler(CommandHandler("when", when))
    app.add_handler(CommandHandler("baby", baby))

    # Планировщик (каждый день в 10:00)
    app.job_queue.run_daily(daily_check, time=datetime.time(hour=10, minute=0))

    app.run_polling()

if __name__ == "__main__":
    main()
