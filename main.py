import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# Инициализация LLM строго для DeepSeek
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_base="https://api.deepseek.com",
    openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
    max_tokens=4096
)

search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# Агенты с явным указанием llm
researcher = Agent(
    role='Market Analyst',
    goal='Провести глубокий анализ рынка',
    backstory='Ты эксперт по маркетингу.',
    tools=[search_tool],
    llm=llm 
)

writer = Agent(
    role='Content Writer',
    goal='Написать вовлекающий пост',
    backstory='Ты профессиональный копирайтер.',
    llm=llm
)

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text("⏳ Агенты начали работу...")
    
    task1 = Task(description=f"Проанализируй: {user_input}", expected_output='Отчет', agent=researcher)
    task2 = Task(description="Напиши пост", expected_output='Пост', agent=writer, context=[task1])
    
    crew = Crew(agents=[researcher, writer], tasks=[task1, task2], process=Process.sequential)
    
    try:
        # Запуск
        result = crew.kickoff()
        await update.message.reply_text(f"📊 Результат:\n\n{result}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    app.run_polling()
