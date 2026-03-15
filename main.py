import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# 1. Принудительно устанавливаем ключ для библиотеки, чтобы она не падала
ds_key = os.getenv("DEEPSEEK_API_KEY")
os.environ["OPENAI_API_KEY"] = ds_key 

# 2. Инициализация DeepSeek
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_base="https://api.deepseek.com",
    openai_api_key=ds_key,
    max_tokens=4096
)

# Инструмент поиска
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# Агенты
researcher = Agent(
    role='Market Analyst',
    goal='Провести глубокий анализ рынка по запросу пользователя',
    backstory='Ты эксперт по маркетингу.',
    tools=[search_tool],
    llm=llm
)

writer = Agent(
    role='Content Writer',
    goal='Написать вовлекающий пост для соцсетей на основе отчета аналитика',
    backstory='Ты профессиональный копирайтер.',
    llm=llm
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой маркетинговый агент на базе DeepSeek. Напиши тему для анализа.")

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"🔍 DeepSeek начинает исследование: '{user_input}'...")
    
    task1 = Task(
        description=f"Проанализируй рынок по теме: {user_input}.",
        expected_output='Подробный отчет на русском языке',
        agent=researcher
    )
    
    task2 = Task(
        description="Напиши вовлекающий пост для Telegram на основе этого отчета.",
        expected_output='Готовый пост с эмодзи на русском языке',
        agent=writer,
        context=[task1]
    )
    
    crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
    
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, crew.kickoff)
        await update.message.reply_text(f"📊 **Результат DeepSeek:**\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при работе агентов: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    app.run_polling()
