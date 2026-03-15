import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Инициализация инструментов
search_tool = SerperDevTool() # Для поиска в Google (новости, статьи, упоминания)
scrape_tool = ScrapeWebsiteTool() # Для чтения конкретных сайтов конкурентов

llm = ChatOpenAI(model="gpt-4o")

# Агент-исследователь (теперь он "видит" всё)
researcher = Agent(
    role='Market Intelligence Analyst',
    goal='Находить упоминания конкурентов в статьях, на форумах и их официальных сайтах',
    backstory='Ты эксперт по конкурентной разведке. Ты умеешь находить скрытую информацию в сети.',
    tools=[search_tool, scrape_tool],
    llm=llm
)

# Агент-стратег (Менеджер)
manager = Agent(
    role='Chief Marketing Officer',
    goal='Анализировать данные от исследователя и давать советы по маркетингу',
    backstory='Ты принимаешь решения на основе данных. Ты видишь общую картину рынка.',
    llm=llm,
    allow_delegation=True
)

# Задача
task_research = Task(
    description="""
    1. Найди в интернете статьи и упоминания конкурентов (название конкурента: 'Конкурент_Х').
    2. Проанализируй их сайты на предмет новых акций или изменений в услугах.
    3. Собери все данные в отчет для CMO.
    """,
    expected_output='Подробный отчет с анализом активности конкурентов.',
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

import os
import requests
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Ваши токены (лучше добавить их в Variables в Railway, как мы делали с ключами)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=data)

# ... (ваш код агентов) ...

if __name__ == "__main__":
    print("--- Система запущена! ---")
    result = marketing_crew.kickoff()
    
    # Отправляем результат в Telegram
    send_telegram_message(f"Отчет агента:\n\n{result}")
    print("--- Работа завершена, отчет отправлен! ---")
