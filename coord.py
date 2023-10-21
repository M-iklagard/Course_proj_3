import aiohttp


async def get_coord(sity_name: str, api_key: str) -> tuple[float, float] | None:
    """Функція звертається до апі, та за назвою міста
     повертає його координати"""

    #  запит
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"http://api.openweathermap.org/geo/1.0/direct?q={sity_name}"
                f"&limit={1}"
                f"&appid={api_key}") as responce:

            # якщо код 200
            if responce.status == 200:
                data = await responce.json()
                if data:
                    lat = data[0]["lat"]
                    lon = data[0]["lon"]

                    print(f"Геолокацю отримано, {sity_name}: [{lat} {lon}]")
                    return lat, lon

            # в іншому випадку
            else:
                print(f"Геолокацю не отримано, {sity_name}: [None]")
                return None
