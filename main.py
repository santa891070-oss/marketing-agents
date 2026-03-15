import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# Проверка ключей при запуске
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")

if not TOKEN or not OPENAI_KEY or not SERPER_KEY:
    print(f"ОШИБКА: Ключи не найдены! TOKEN={bool(TOKEN)}, OPENAI={bool(OPENAI_KEY)}, SERPER={bool(SERPER_KEY)}")
    exit(1)

async def start(update, context):
    await update.message.reply_text("Бот запущен и готов к работе!")

async def main():
    print("Запуск бота...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    print("Бот успешно запущен в режиме polling!")
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
