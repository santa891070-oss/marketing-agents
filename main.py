logger.info("=== DEBUG ENV VARS на Railway ===")
for k, v in sorted(os.environ.items()):
    if 'TOKEN' in k.upper() or 'KEY' in k.upper() or 'API' in k.upper():
        masked = (v[:6] + '...' + v[-6:]) if v else 'None / пусто'
        logger.info(f"{k} → {masked}")
logger.info("=== DEBUG конец ===")
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

# CrewAI / Langchain импорты (раскомментируй по мере необходимости)
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# ────────────────────────────────────────────────
# Настройка логирования
# ────────────────────────────────────────────────

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────
# Загрузка переменных окружения
# ────────────────────────────────────────────────

load_dotenv()  # поддержка .env файла (удобно локально)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

missing = []
if not TELEGRAM_TOKEN: missing.append("TELEGRAM_TOKEN")
if not OPENAI_API_KEY: missing.append("OPENAI_API_KEY")
if not SERPER_API_KEY: missing.append("SERPER_API_KEY")

if missing:
    logger.error("Отсутствуют переменные: " + ", ".join(missing))
    logger.error("Проверьте настройки Environment в Render Dashboard")
    exit(1)

logger.info("Все ключи найдены, продолжаем запуск...")


# ────────────────────────────────────────────────
# Простой handler /start
# ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Бот запущен!\n\n"
        "Пока умею только здороваться 😄\n"
        "Напиши что-нибудь — я пока просто повторю."
    )


# ────────────────────────────────────────────────
# Эхо-handler (для теста, потом заменишь на CrewAI логику)
# ────────────────────────────────────────────────

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text(f"Ты написал: {text}")


# ────────────────────────────────────────────────
# Здесь можно добавить CrewAI-логику
# ────────────────────────────────────────────────

# Пример: как может выглядеть запуск Crew при получении сообщения
async def handle_message_with_crew(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Пример минимальной CrewAI-структуры (раскомментируй и адаптируй)
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    researcher = Agent(
        role="Исследователь",
        goal="Искать актуальную информацию",
        backstory="Ты эксперт по поиску в интернете",
        tools=[SerperDevTool()],
        llm=llm,
        verbose=True
    )

    task = Task(
        description=f"Найди краткую информацию по запросу: {user_message}",
        expected_output="Короткий и точный ответ",
        agent=researcher
    )

    crew = Crew(agents=[researcher], tasks=[task], verbose=2)
    result = crew.kickoff()
    
    await update.message.reply_text(str(result))
    """

    # Пока просто эхо (удали когда добавишь Crew)
    await update.message.reply_text(f"Получено: {user_message}\n(пока без CrewAI)")


# ────────────────────────────────────────────────
# Главная функция
# ────────────────────────────────────────────────

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

    # Команды
    application.add_handler(CommandHandler("start", start))

    # Все текстовые сообщения (кроме команд)
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
