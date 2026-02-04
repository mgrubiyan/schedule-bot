from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select
from database.models import async_session, User
from services.parser import get_real_schedule, get_today_schedule

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            # Регистрируем нового юзера
            new_user = User(id=message.from_user.id, username=message.from_user.username)
            session.add(new_user)
            await session.commit()

    await message.answer(
        f"Привет, {message.from_user.full_name}! Я тебя запомнил.\n"
        "Теперь я буду присылать тебе уведомления за 40 минут до первой пары.\n"
        "Доступные команды:\n"
        "/today — расписание на сегодня\n"
        "/schedule — расписание на неделю"
    )


@router.message(Command("today"))
async def cmd_today(message: types.Message):
    await message.answer("🔍 Ищу пары на сегодня...")
    schedule = await get_today_schedule()

    if not schedule:
        await message.answer("🎉 На сегодня пар нет! Можно отдыхать.")
        return

    text = "📅 **Расписание на сегодня:**\n\n"
    for lesson in schedule:
        text += f"⏰ {lesson['time']} | 📍 {lesson['room']}\n📖 {lesson['subject']}\n\n"

    await message.answer(text, parse_mode="Markdown")


@router.message(Command("schedule"))
async def cmd_schedule(message: types.Message):
    await message.answer("⏳ Гружу полное расписание...")
    lessons = await get_real_schedule()

    if not lessons:
        await message.answer("😔 Расписание пустое.")
        return

    text = ""
    current_day = ""

    for lesson in lessons:
        if lesson['date'] != current_day:
            current_day = lesson['date']
            text += f"\n📅 **{current_day}**\n"

        text += f"⏰ {lesson['time']} | {lesson['room']}\n📖 {lesson['subject']}\n\n"

    if len(text) > 4000:
        text = text[:4000] + "... (обрезано)"

    await message.answer(text, parse_mode="Markdown")
