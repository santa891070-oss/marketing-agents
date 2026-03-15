import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI

# Инициализация инструментов и LLM
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# Определение агента
researcher = Agent(
    role='Market Analyst',
    goal='Провести глубокий анализ рынка по запросу пользователя',
    backstory='Ты опытный маркетинговый аналитик, который находит лучшие инсайты.',
    tools=[search_tool],
    llm=llm
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой маркетинговый агент. Напиши тему, и я проведу анализ рынка для тебя.")

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"🔍 Ищу информацию и анализирую: '{user_input}'...")
    
    # Создаем задачу
    task = Task(
        description=f"Проанализируй рынок по теме: {user_input}. Выдай основные тренды, конкурентов и рекомендации.",
        expected_output='Подробный маркетинговый отчет на русском языке',
        agent=researcher
    )
    
    # Создаем команду (Crew)
    crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential)
    
    # Запуск (выполняем в отдельном потоке, чтобы не блокировать бота)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, crew.kickoff)
    
    await update.message.reply_text(f"📊 **Результат анализа:**\n\n{result}")

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    
    print("Бот готов к работе!")
    app.run_polling()
