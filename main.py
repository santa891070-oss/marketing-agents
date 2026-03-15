import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI # ВОТ ЭТОГО СТРОКИ НЕ ХВАТАЛО

# Инициализация LLM
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
search_tool = SerperDevTool(api_key=os.getenv("SERPER_API_KEY"))

# Агент
researcher = Agent(
    role='Market Analyst',
    goal='Анализ рынка и конкурентов',
    backstory='Ты эксперт по маркетингу.',
    tools=[search_tool],
    llm=llm
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой маркетинговый агент. Напиши тему, и я проведу анализ.")

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"🔍 Ищу информацию по: {user_input}...")
    
    task = Task(description=user_input, expected_output='Подробный отчет', agent=researcher)
    crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential)
    
    result = crew.kickoff()
    await update.message.reply_text(f"📊 Результат анализа:\n\n{result}")

if __name__ == '__main__':
    # Запуск бота
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    
    print("Бот запущен и ждет команд...")
    app.run_polling()
