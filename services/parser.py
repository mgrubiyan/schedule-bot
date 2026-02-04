import aiohttp
from bs4 import BeautifulSoup, NavigableString
import logging
from datetime import datetime
import re

SCHEDULE_URL = "https://rasp.unecon.ru/raspisanie_grp.php?g=13825"
HEADERS = {"User-Agent": "Mozilla/5.0"}


async def fetch_schedule_html() -> str:
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            async with session.get(SCHEDULE_URL, headers=HEADERS) as response:
                return await response.text() if response.status == 200 else ""
        except Exception:
            return ""


def get_clean_text_from_tag(tag) -> str:
    """
    Извлекает текст только из видимых частей, игнорируя скрытые спаны.
    Берет только ПЕРВУЮ значимую строку.
    """
    if not tag: return ""

    # Удаляем мусор прямо в копии тега
    tag_copy = BeautifulSoup(str(tag), "html.parser")
    for hidden in tag_copy.find_all(class_="scheme"):  # Класс скрытых ссылок на схему
        hidden.decompose()
    for trash in tag_copy.find_all(string=re.compile("ПОКАЗАТЬ НА СХЕМЕ")):
        trash.parent.decompose()

    # Теперь берем текст. Если там были <br>, они склеятся.
    # Но мы возьмем только первую часть до разделителя |
    text = tag_copy.get_text(separator=" ", strip=True)

    # Режем по разделителю палки (если он есть)
    if "|" in text:
        text = text.split("|")[0]

    return text.strip()


def clean_subject(subject_text: str) -> str:
    """Чистит предмет от времени и аудитории"""
    subject_text = re.sub(r'\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}', '', subject_text)
    subject_text = re.sub(r'\d+\s*ауд\.?', '', subject_text)
    subject_text = subject_text.replace("Грибоедова 30/32", "").replace("Грибоедова", "")
    subject_text = subject_text.replace("|", "")
    return re.sub(r'\s+', ' ', subject_text).strip()


def parse_schedule_from_html(html_content: str) -> list[dict]:
    if not html_content: return []
    soup = BeautifulSoup(html_content, "html.parser")
    schedule = []

    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if not cols: continue

        # ВАЖНО: Мы не берем текст сразу. Мы смотрим на колонки.
        current_date = "Неизвестная дата"
        time = ""
        room = ""
        subject = ""

        # Определяем тип строки
        col_texts = [get_clean_text_from_tag(c) for c in cols]

        # Логика 1: Дата + Пара
        if len(col_texts) >= 4 and "." in col_texts[0]:
            current_date = col_texts[0]
            time = col_texts[1]
            room = col_texts[2]  # get_clean_text_from_tag уже обрезал по |
            subject = col_texts[3]

        # Логика 2: Только Пара
        elif len(col_texts) >= 3 and ":" in col_texts[0]:
            time = col_texts[0]
            room = col_texts[1]
            subject = col_texts[2]
        else:
            continue

        if not time or not subject: continue

        # Финальная полировка
        room = re.sub(r'\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}', '', room).strip()
        subject = clean_subject(subject)

        # Исправление даты (пробел перед днем недели)
        if len(current_date) > 10 and current_date[10] != ' ':
            current_date = current_date[:10] + ' ' + current_date[10:]

        schedule.append({
            "date": current_date,
            "time": time,
            "subject": subject,
            "room": room
        })

    return schedule


async def get_real_schedule() -> list[dict]:
    html = await fetch_schedule_html()
    return parse_schedule_from_html(html)


async def get_today_schedule() -> list[dict]:
    full = await get_real_schedule()
    today = datetime.now().strftime("%d.%m.%Y")
    return [s for s in full if today in s['date']]
