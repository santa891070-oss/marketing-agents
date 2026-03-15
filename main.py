import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# Инициализация LLM
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# 1. Агент-исследователь
researcher = Agent(
    role='Market Analyst',
    goal='Провести глубокий анализ рынка по запросу пользователя',
    backstory='Ты эксперт по маркетингу, который находит лучшие инсайты и конкурентов.',
    tools=[search_tool],
    llm=llm
)

# 2. Агент-копирайтер
writer = Agent(
    role='Content Writer',
    goal='Написать вовлекающий пост для соцсетей на основе отчета аналитика',
    backstory='Ты профессиональный копирайтер, который умеет переводить сложные данные в простой и продающий текст.',
    llm=llm
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой маркетинговый агент. Напиши тему, и я проведу анализ и напишу пост!")

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"🔍 Начинаю исследование: '{user_input}'...")
    
    # Задача 1: Исследование
    task1 = Task(
        description=f"Проанализируй рынок по теме: {user_input}. Выдай основные тренды и конкурентов.",
        expected_output='Подробный отчет с фактами и цифрами на русском языке',
        agent=researcher
    )
    
    # Задача 2: Написание поста
    task2 = Task(
        description="Напиши вовлекающий пост для Telegram на основе отчета аналитика.",
        expected_output='Готовый пост с эмодзи и призывом к действию на русском языке',
        agent=writer,
        context=[task1] # Передаем результат первого задания второму
    )
    
    # Создаем команду
    crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
    
    # Запуск
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, crew.kickoff)
    
    await update.message.reply_text(f"📊 **Результат анализа и пост:**\n\n{result}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    app.run_polling()
