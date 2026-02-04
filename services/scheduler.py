import logging
from datetime import datetime, timedelta
from aiogram import Bot
from sqlalchemy import select
from database.models import async_session, User
from services.parser import get_today_schedule


async def check_and_notify(bot: Bot):
    """
    Запускается каждую минуту.
    Проверяет, осталось ли ровно 40 минут до первой пары.
    """
    try:
        # 1. Получаем пары на сегодня
        today_lessons = await get_today_schedule()
        if not today_lessons:
            return

            # 2. Берем первую пару (самую раннюю)
        first_lesson = today_lessons[0]

        # 3. Парсим время начала (из строки "12:40 - 14:15")
        start_time_str = first_lesson['time'].split(" - ")[0]  # "12:40"
        lesson_hour, lesson_minute = map(int, start_time_str.split(":"))

        now = datetime.now()
        # Создаем объект времени начала пары на СЕГОДНЯ
        lesson_start = now.replace(hour=lesson_hour, minute=lesson_minute, second=0, microsecond=0)

        # 4. Считаем, сколько осталось
        time_to_lesson = lesson_start - now

        # 5. Условие срабатывания: осталось от 39 до 40 минут
        if timedelta(minutes=39) <= time_to_lesson < timedelta(minutes=40):
            logging.info("Время пришло! Рассылаю уведомления.")

            # Достаем всех юзеров из БД
            async with async_session() as session:
                users_result = await session.execute(select(User))
                users = users_result.scalars().all()

                for user in users:
                    try:
                        await bot.send_message(
                            user.id,
                            f"🏃‍♂️ **ПОРА ВЫХОДИТЬ!**\n\n"
                            f"Через 40 минут начало: **{first_lesson['subject']}**\n"
                            f"📍 Аудитория: {first_lesson['room']}"
                        )
                    except Exception as e:
                        logging.error(f"Не удалось отправить юзеру {user.id}: {e}")

    except Exception as e:
        logging.error(f"Ошибка в планировщике: {e}")
