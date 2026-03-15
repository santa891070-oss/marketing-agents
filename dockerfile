FROM python:3.11-slim

# Оптимизации для контейнера
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Сначала зависимости — для лучшего кэширования слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Запуск без буферизации вывода (логи видны сразу)
CMD ["python", "-u", "main.py"]
