import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Явно берем ключи из переменных среды
openai_api_key = os.getenv("OPENAI_API_KEY")
serper_api_key = os.getenv("SERPER_API_KEY")

# Проверка, что ключи вообще загрузились
if not openai_api_key:
    raise ValueError("ОШИБКА: Переменная OPENAI_API_KEY не найдена в Railway!")

# Инициализация LLM с явной передачей ключа
llm = ChatOpenAI(
    model="gpt-4o", 
    api_key=openai_api_key
)

# Инструменты
search_tool = SerperDevTool(api_key=serper_api_key)
scrape_tool = ScrapeWebsiteTool()

# Агенты
researcher = Agent(
    role='Market Intelligence Analyst',
    goal='Находить упоминания конкурентов и анализировать их сайты',
    backstory='Ты эксперт по конкурентной разведке.',
    tools=[search_tool, scrape_tool],
    llm=llm
)

manager = Agent(
    role='Chief Marketing Officer',
    goal='Анализировать данные и давать советы',
    backstory='Ты принимаешь решения на основе данных.',
    llm=llm,
    allow_delegation=True
)

# Задача
task_research = Task(
    description="Проанализируй рынок и найди упоминания конкурентов.",
    expected_output='Отчет с анализом.',
    agent=researcher
)

marketing_crew = Crew(
    agents=[manager, researcher],
    tasks=[task_research],
    process=Process.hierarchical,
    manager_llm=llm
)

if __name__ == "__main__":
    marketing_crew.kickoff()

import time

if __name__ == "__main__":
    while True:
        print("Начинаю цикл маркетингового анализа...")
        marketing_crew.kickoff()
        print("Цикл завершен. Сплю 24 часа.")
        time.sleep(86400) # Сон на сутки
