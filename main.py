import os
import asyncio
import logging
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# CrewAI / Langchain импорты
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# ================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ (ОБЯЗАТЕЛЬНО ПЕРЕД ВСЕМ!)
# ================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================================
# DEBUG: Показываем все env-переменные (для Railway)
# ================================================
logger.info("=== DEBUG ENV VARS НА RAILWAY ===")
for k, v in sorted(os.environ.items()):
    if any(x in k.upper() for x in ['TOKEN', 'KEY', 'API', 'SERPER', 'OPENAI', 'TELEGRAM']):
        masked = (v[:8] + '...' + v[-8:]) if v and len(v) > 16 else (v or 'None / пусто')
        logger.info(f"{k:25} → {masked}")
logger.info("=== DEBUG КОНЕЦ ===")
logger.info("")

# ================================================
# Загрузка переменных окружения
# ================================================
load_dotenv()  # поддержка .env локально

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

missing = []
if not TELEGRAM_TOKEN: missing.append("TELEGRAM_TOKEN")
if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
if not SERPER_API_KEY: missing.append("SERPER_API_KEY")

if missing:
    logger.error("Отсутствуют переменные: " + ", ".join(missing))
    logger.error("Проверьте Variables в Railway Dashboard")
    exit(1)

logger.info("Все ключи найдены, продолжаем запуск...")

# ================================================
# Handlers
# ================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот запущен!\n\n"
        "Пока умею только здороваться 😄\n"
        "Напиши что-нибудь — я пока просто повторю."
    )

async def handle_message_with_crew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # ← Здесь будет CrewAI (пока просто эхо)
    await update.message.reply_text(f"Получено: {user_message}\n(пока без CrewAI)")

# ================================================
# Главная функция
# ================================================
async def main():
    logger.info("Запуск Telegram-бота...")
    
    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .get_updates_connect_timeout(10)
        .get_updates_read_timeout(10)
        .get_updates_write_timeout(10)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_with_crew)
    )

    logger.info("Polling запущен...")

    await application.run_polling(
        drop_pending_updates=True,
        poll_interval=0.5,
        timeout=10,
        bootstrap_retries=-1,
    )


if __name__ == "__main__":
    asyncio.run(main())
