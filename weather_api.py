import aiohttp


async def get_weather(coordinates: tuple, language_code: str, api_key: str) -> dict | None:
    """
    Функція робить запит до погодного api openweathermap
    та повертає dict, або None
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"https://api.openweathermap.org/data/3.0/onecall?"
                f"lat={coordinates[0]}"
                f"&lon={coordinates[1]}"
                f"&units=metric"
                f"&lang={language_code}"
                f"&exclude=hourly,minutely"
                f"&appid={api_key}"
        ) as response:

            # якщо дані отримані, то зберегти їх у змінну
            if response.status == 200:
                data = await response.json()
                print("Дані отримані")
                return data
            else:
                print("Дані не отримані, помилка з боку апі")
                return None

