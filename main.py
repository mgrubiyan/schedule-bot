import asyncio
import logging
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database.models import init_db
from handlers import user_handlers
from services.scheduler import check_and_notify

logging.basicConfig(level=logging.INFO)


async def main():
    print("🚀 Запускаю бота UNECON Schedule...")

    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user_handlers.router)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_and_notify, 'interval', minutes=1, kwargs={"bot": bot})
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Боту похуй.")
