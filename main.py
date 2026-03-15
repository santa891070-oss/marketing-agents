import os
import asyncio
import logging
import warnings
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# CrewAI пока закомментированы
# from crewai import Agent, Task, Crew
# from crewai_tools import SerperDevTool
# from langchain_openai import ChatOpenAI

# ================================================
# Логирование + отключение раздражающих предупреждений
# ================================================
warnings.simplefilter("ignore", RuntimeWarning)   # скрываем "was never awaited"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================================================
# DEBUG ENV
# ================================================
logger.info("=== DEBUG ENV VARS НА RAILWAY ===")
for k, v in sorted(os.environ.items()):
    if any(x in k.upper() for x in ['TOKEN', 'KEY', 'API', 'SERPER', 'OPENAI', 'TELEGRAM']):
        masked = (v[:8] + '...' + v[-8:]) if v and len(v) > 16 else (v or 'None / пусто')
        logger.info(f"{k:25} → {masked}")
logger.info("=== DEBUG КОНЕЦ ===\n")

# ================================================
# Переменные
# ================================================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, SERPER_API_KEY]):
    logger.error("Отсутствуют ключи!")
    exit(1)

logger.info("Все ключи найдены → запускаем бота...")

# ================================================
# Handlers
# ================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот онлайн! Напиши что угодно.")

async def handle_message_with_crew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Получено: {update.message.text}\n(пока без CrewAI)")

# ================================================
# Главная функция (упрощённая для Railway)
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

    # Самый стабильный вариант для платформ, которые убивают контейнер
    await application.run_polling(
        drop_pending_updates=True,
        poll_interval=0.5,
        timeout=10,
        bootstrap_retries=-1,
        stop_signals=None,          # важно!
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (RuntimeError, asyncio.CancelledError) as e:
        if any(x in str(e).lower() for x in ["event loop", "never awaited", "not running", "shutdown"]):
            logger.info("Бот остановлен Railway (нормально, без ошибки)")
        else:
            raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        raise
