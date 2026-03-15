import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Инициализация агентов (вне функций, чтобы они были доступны)
search_tool = SerperDevTool()
llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

researcher = Agent(role='Researcher', goal='Анализ рынка', backstory='Ты эксперт.', tools=[search_tool], llm=llm)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я маркетинговый агент. Пришли мне тему для анализа, и я запущу исследование.")

async def run_agent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text(f"Принято! Запускаю анализ по теме: {user_input}...")
    
    # Создаем задачу на лету
    task = Task(description=user_input, expected_output='Отчет', agent=researcher)
    crew = Crew(agents=[researcher], tasks=[task], process=Process.sequential)
    
    result = crew.kickoff()
    await update.message.reply_text(f"Результат анализа:\n\n{result}")

if __name__ == '__main__':
    # Запуск бота
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    app.add_handler(CommandHandler("start", start))
    # Обработчик любого текста (кроме команд)
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, run_agent))
    
    print("Бот запущен и ждет команд...")
    app.run_polling()
