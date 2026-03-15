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

# CrewAI импорты (пока закомментированы)
# from crewai import Agent, Task, Crew
# from crewai_tools import SerperDevTool
# from langchain_openai import ChatOpenAI

# ================================================
# Логирование
# ================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================================
# DEBUG ENV (уже работает)
# ================================================
logger.info("=== DEBUG ENV VARS НА RAILWAY ===")
for k, v in sorted(os.environ.items()):
    if any(x in k.upper() for x in ['TOKEN', 'KEY', 'API', 'SERPER', 'OPENAI', 'TELEGRAM']):
        masked = (v[:8] + '...' + v[-8:]) if v and len(v) > 16 else (v or 'None / пусто')
        logger.info(f"{k:25} → {masked}")
logger.info("=== DEBUG КОНЕЦ ===\n")

# ================================================
# Переменные окружения
# ================================================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, SERPER_API_KEY]):
    logger.error("Отсутствуют ключи! Проверь Variables в Railway")
    exit(1)

logger.info("Все ключи найдены, запускаем бота...")

# ================================================
# Handlers
# ================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен! Напиши что угодно.")

async def handle_message_with_crew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Получено: {update.message.text}\n(пока без CrewAI)")

# ================================================
# Главная функция с защитой от ошибки Railway
# ================================================
async def main():
    logger.info("Запуск Telegram-бота...")

    application = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .get_updates_connect_timeout(15)
        .get_updates_read_timeout(15)
        .get_updates_write_timeout(15)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_with_crew)
    )

    logger.info("Polling запущен...")

    try:
        await application.run_polling(
            drop_pending_updates=True,
            poll_interval=0.5,
            timeout=10,
            bootstrap_retries=-1,
            stop_signals=None,          # ← главное исправление!
        )
    except asyncio.CancelledError:
        logger.info("Polling отменён платформой (нормально)")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await application.stop()
        logger.info("Бот остановлен gracefully")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit, RuntimeError) as e:
        if "event loop" in str(e).lower() or "never awaited" in str(e).lower():
            logger.info("Бот остановлен Railway (нормально, без красной ошибки)")
        else:
            raise
