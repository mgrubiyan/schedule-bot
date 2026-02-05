import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
import re

SCHEDULE_URL = "https://rasp.unecon.ru/raspisanie_grp.php?g=13825"
HEADERS = {"User-Agent": "Mozilla/5.0"}


async def fetch_schedule_html() -> str:
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(SCHEDULE_URL, headers=HEADERS) as response:
            return await response.text() if response.status == 200 else ""


def clean_text(text: str) -> str:
    text = re.sub(r'ПОКАЗАТЬ НА СХЕМЕ', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_schedule_from_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    schedule = []

    current_date = None

    for row in soup.find_all("tr"):
        cells = [clean_text(td.get_text(" ", strip=True)) for td in row.find_all("td")]
        if not cells:
            continue

        # 🔹 если в строке есть дата — обновляем состояние
        if re.match(r"\d{2}\.\d{2}\.\d{4}", cells[0]):
            current_date = cells[0][:10]
            cells = cells[1:]  # убираем дату из обработки

        # 🔹 ищем время пары
        time_cell = next((c for c in cells if re.search(r"\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}", c)), None)
        if not time_cell or not current_date:
            continue

        time = re.search(r"\d{1,2}:\d{2}\s*-\s*\d{1,2}:\d{2}", time_cell).group()

        # 🔹 собираем остальной текст как описание
        rest_text = " ".join(cells)
        rest_text = rest_text.replace(time, "").strip()

        schedule.append({
            "date": current_date,
            "time": time,
            "text": rest_text
        })

    return schedule


async def get_real_schedule() -> list[dict]:
    html = await fetch_schedule_html()
    return parse_schedule_from_html(html)


async def get_today_schedule() -> list[dict]:
    full = await get_real_schedule()
    today = datetime.now().strftime("%d.%m.%Y")
    return sorted(
        [s for s in full if s["date"] == today],
        key=lambda x: x["time"]
    )