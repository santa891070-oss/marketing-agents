import os
import sys
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# 1. ДИАГНОСТИКА: Выводим в лог, видит ли система ключи
print(f"--- DEBUG: OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))} ---")
print(f"--- DEBUG: SERPER_API_KEY exists: {bool(os.getenv('SERPER_API_KEY'))} ---")

# 2. Получение ключей
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

# 3. Проверка ключей
if not openai_api_key:
    print("ОШИБКА: Переменная OPENAI_API_KEY не найдена!")
    print("Доступные переменные среды:", list(os.environ.keys()))
    sys.exit(1) # Останавливаем программу, если ключа нет

# 4. Инициализация
llm = ChatOpenAI(model="gpt-4o", api_key=openai_api_key)
search_tool = SerperDevTool(api_key=serper_api_key)
scrape_tool = ScrapeWebsiteTool()

# 5. Агенты
researcher = Agent(
    role='Market Intelligence Analyst',
    goal='Анализ конкурентов и поиск упоминаний в сети',
    backstory='Ты эксперт по конкурентной разведке. Ты находишь информацию везде.',
    tools=[search_tool, scrape_tool],
    llm=llm
)

manager = Agent(
    role='Chief Marketing Officer',
    goal='Разработка стратегии на основе данных',
    backstory='Ты принимаешь решения на основе данных от исследователя.',
    llm=llm,
    allow_delegation=True
)

# 6. Задача
task_research = Task(
    description="Проанализируй текущую ситуацию на рынке по нашей нише, найди упоминания конкурентов и подготовь краткий отчет.",
    expected_output='Отчет с анализом рынка.',
    agent=researcher
)

# 7. Команда
marketing_crew = Crew(
    agents=[manager, researcher],
    tasks=[task_research],
    process=Process.hierarchical,
    manager_llm=llm
)

if __name__ == "__main__":
    print("--- Система запущена! ---")
    marketing_crew.kickoff()
    print("--- Работа завершена! ---")
