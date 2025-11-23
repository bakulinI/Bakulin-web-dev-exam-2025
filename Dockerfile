# Используем базовый образ Python 3.11 slim
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (для MySQL connector могут понадобиться)
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения
COPY . .

# Создаем директорию для uploads, если её нет
RUN mkdir -p /app/app/static/uploads

# Создаем файл config.py из переменных окружения или с дефолтными значениями
RUN echo "import os\n\
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')\n\
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')\n\
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')\n\
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'password')\n\
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'bakulinexam')\n\
" > /app/app/config.py

# Открываем порт для Flask приложения
EXPOSE 5000

# Устанавливаем переменные окружения для Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Команда для запуска приложения
CMD ["python", "run.py"]

