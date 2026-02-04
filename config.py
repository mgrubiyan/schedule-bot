import os
from pathlib import Path
from dotenv import load_dotenv

# Получаем путь к папке, где лежит config.py (это корень твоего проекта)
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = BASE_DIR / ".env"

print(f"--- DEBUG INFO ---")
print(f"1. Папка проекта: {BASE_DIR}")
print(f"2. Ищу .env файл здесь: {ENV_FILE_PATH}")
print(f"3. Файл существует? {'ДА' if ENV_FILE_PATH.exists() else 'НЕТ'}")

# Принудительно загружаем именно этот файл
load_dotenv(dotenv_path=ENV_FILE_PATH)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"4. Токен загружен? {'ДА' if BOT_TOKEN else 'НЕТ'}")
print(f"------------------")

if not BOT_TOKEN:
    raise ValueError("ОШИБКА: Токен не найден! Проверь файл .env (убедись, что нет пробелов и имя переменной BOT_TOKEN)")
