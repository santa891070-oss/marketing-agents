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

if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, SERPER_API_KEY]):
    logger.error("Не все обязательные переменные окружения заданы!")
    logger.error(f"TELEGRAM_TOKEN  → {bool(TELEGRAM_TOKEN)}")
    logger.error(f"OPENAI_API_KEY  → {bool(OPENAI_API_KEY)}")
    logger.error(f"SERPER_API_KEY  → {bool(SERPER_API_KEY)}")
    exit(1)

# Устанавливаем ключи для библиотек
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["SERPER_API_KEY"] = SERPER_API_KEY


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
