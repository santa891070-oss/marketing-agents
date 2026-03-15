import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
# from crewai import Agent, Task, Crew, Process           # пока не используются
# from crewai_tools import SerperDevTool
# from langchain_openai import ChatOpenAI

# ────────────────────────────────────────────────
# Проверка ключей
# ────────────────────────────────────────────────

TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")

if not all([TOKEN, OPENAI_KEY, SERPER_KEY]):
    print("ОШИБКА: Не все ключи заданы!")
    print(f"TELEGRAM_TOKEN  → {bool(TOKEN)}")
    print(f"OPENAI_API_KEY  → {bool(OPENAI_KEY)}")
    print(f"SERPER_API_KEY  → {bool(SERPER_KEY)}")
    exit(1)


async def start(update, context):
    await update.message.reply_text("Бот запущен и готов к работе! 🚀")


async def main():
    print("Запуск бота...")

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .get_updates_connect_timeout(10)
        .get_updates_read_timeout(10)
        .get_updates_write_timeout(10)
        .build()
    )

    application.add_handler(CommandHandler("start", start))

    # ─── здесь потом добавишь CrewAI / агентов / инструменты ───
    # например:
    # os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    # os.environ["SERPER_API_KEY"] = SERPER_KEY
    # ...

    print("Бот стартует polling...")
    
    # Самый правильный способ в v20+
    await application.run_polling(
        drop_pending_updates=True,   # полезно при перезапуске
        allowed_updates=["message", "callback_query"]
    )


if __name__ == "__main__":
    asyncio.run(main())
