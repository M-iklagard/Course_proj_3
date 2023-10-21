from weather_api import get_weather
import datetime
from aiogram import types


async def show_current_weather(coords: tuple, api_key: str, message: types.message):
    """Функція формує повідомлення з даними поточної погоди,
    та надсилає у телеграм"""

    # надсилаємо запит, для отримання погодних даних
    data = await get_weather(coords, "ua", api_key)
    text = ""

    # структура відповіді не постійна, тому виконуємо такий перебор та порівняння
    if data:
        for name, val in data["current"].items():
            match name:
                case "dt":
                    text += (f"дата 🗓: {datetime.datetime.fromtimestamp(val).date()}"
                             f"- {data['current']['weather'][0]['description']}\n\n")
                case "sunrise":
                    text += f"схід сонця ☀️: {datetime.datetime.fromtimestamp(val).time()}\n"
                case "sunset":
                    text += f"захід сонця ⛅️: {datetime.datetime.fromtimestamp(val).time()}\n\n"
                case "temp":
                    text += f"температура 🌡: {val} °С "
                case "feels_like":
                    text += f" відчувається як: {val} °С\n"
                case "pressure":
                    text += f"атмосферний тиск 🏋️‍♀️: {val}\n"
                case "humidity":
                    text += f"вологість 💧: {val} %\n"
                case "dew_point":
                    text += f"температура конденсації 💦: {val} °С\n"
                case "uvi":
                    text += f"ультрафіолетове випромінювання: {val} \n"
                case "clouds":
                    text += f"хмарність: {val} %\n\n"
                case "wind_speed":
                    text += f"швидкість вітру: {val} м/с\n"
                case "wind_deg":
                    #  для більш наочного відображення напрямку вітру
                    directions = ["Північ", "Північний схід",
                                  "Схід", "Південний схід",
                                  "Південь", "Південний захід",
                                  "Захід", "Північний захід"]

                    index = round(val / 45) % 8
                    direction = directions[index]
                    text += f"напрямок вітру: {direction} \n"

                case "wind_gust":
                    text += f"пориви вітру до: {val} м/с\n"

        await message.answer(text)

    else:
        await message.answer("Дані не знайдено")


async def show_forecast(coords: tuple, api_key: str, message: types.message):
    """Для кожного дня функція формує повідомлення з даними поточної погоди,
    та надсилає як повідомлення у телеграм"""

    data = await get_weather(coords, "ua", api_key)

    #  якщо дані існують
    if data:
        #  ітеруємось крізь дні
        for day in data["daily"]:
            text = ""

            #  ітеруємось крізь дані днів, та формуємо повідомлення
            for key, val in day.items():
                match key:
                    case "dt":
                        text += (f"дата 🗓: {datetime.datetime.fromtimestamp(val).date()}"
                                 f"- {day['weather'][0]['description']}\n\n")
                    case "sunrise":
                        text += f"схід сонця ☀️: {datetime.datetime.fromtimestamp(val).time()}\n"
                    case "sunset":
                        text += f"захід сонця ⛅️: {datetime.datetime.fromtimestamp(val).time()}\n"
                    case "moonrise":
                        text += f"схід місяця 🌕: {datetime.datetime.fromtimestamp(val).time()}\n"
                    case "moonset":
                        text += f"захід місяця 🌑: {datetime.datetime.fromtimestamp(val).time()}\n"
                    case "moon_phase":
                        text += f"фаза місяця 🌑: {val}\n\n"

                    case "temp":
                        text += (f"Температура:\n\n"
                                 f"день:{val['day']}  відчувається як  {day['feels_like']['day']}\n"
                                 f"ніч:{val['night']}  відчувається як  {day['feels_like']['night']}\n"
                                 f"вечір:{val['eve']}  відчувається як  {day['feels_like']['eve']}\n"
                                 f"ранок:{val['morn']}  відчувається як  {day['feels_like']['morn']}\n\n")

                    case "pressure":
                        text += f"атмосферний тиск 🏋️‍♀️: {val}\n"
                    case "humidity":
                        text += f"вологість 💧: {val} %\n"
                    case "dew_point":
                        text += f"температура конденсації 💦: {val} °С\n"
                    case "wind_deg":
                        #  для більш наочного відображення напрямку вітру
                        directions = ["Північ", "Північний схід",
                                      "Схід", "Південний схід",
                                      "Південь", "Південний захід",
                                      "Захід", "Північний захід"]

                        index = round(val / 45) % 8
                        direction = directions[index]
                        text += f"напрямок вітру: {direction} \n"

                    case "wind_gust":
                        text += f"пориви вітру до: {val} м/с\n"
                    case "clouds":
                        text += f"хмарність: {val} %\n"
                    case "uvi":
                        text += f"ультрафіолетове випромінювання: {val} \n"

            await message.answer(text)
    else:
        await message.answer("Дані не знайдено")


async def show_forecast_by_date(coords: tuple, api_key: str, message: types.message, date: str):
    """Функція формує повідомлення з даними поточної погоди за певний день,
     введений користувачем, та надсилає у телеграм"""

    # робимо запрос до апі погоди
    data = await get_weather(coords, "ua", api_key)

    if data:

        #  перебираємо кожен день із даних
        for day in data["daily"]:

            #  якщо дата дня збігається з вводом користувача, формуємо відповідь
            if str(datetime.datetime.fromtimestamp(day["dt"]).date()) == date:
                text = ""

                # структура відповіді не постійна, тому виконуємо такий перебор та порівняння
                for key, val in day.items():
                    match key:
                        case "dt":
                            text += (f"дата 🗓: {datetime.datetime.fromtimestamp(val).date()}"
                                     f"- {day['weather'][0]['description']}\n\n")
                        case "sunrise":
                            text += f"схід сонця ☀️: {datetime.datetime.fromtimestamp(val).time()}\n"
                        case "sunset":
                            text += f"захід сонця ⛅️: {datetime.datetime.fromtimestamp(val).time()}\n"
                        case "moonrise":
                            text += f"схід місяця 🌕: {datetime.datetime.fromtimestamp(val).time()}\n"
                        case "moonset":
                            text += f"захід місяця 🌑: {datetime.datetime.fromtimestamp(val).time()}\n"
                        case "moon_phase":
                            text += f"фаза місяця 🌑: {val}\n\n"

                        case "temp":
                            text += (f"Температура:\n\n"
                                     f"день:{val['day']}  відчувається як  {day['feels_like']['day']}\n"
                                     f"ніч:{val['night']}  відчувається як  {day['feels_like']['night']}\n"
                                     f"вечір:{val['eve']}  відчувається як  {day['feels_like']['eve']}\n"
                                     f"ранок:{val['morn']}  відчувається як  {day['feels_like']['morn']}\n\n")

                        case "pressure":
                            text += f"атмосферний тиск 🏋️‍♀️: {val}\n"
                        case "humidity":
                            text += f"вологість 💧: {val} %\n"
                        case "dew_point":
                            text += f"температура конденсації 💦: {val} °С\n"
                        case "wind_deg":
                            #  більш наочне відображення напрямку вітру
                            directions = ["Північ", "Північний схід",
                                          "Схід", "Південний схід",
                                          "Південь", "Південний захід",
                                          "Захід", "Північний захід"]

                            index = round(val / 45) % 8
                            direction = directions[index]
                            text += f"напрямок вітру: {direction} \n"

                        case "wind_gust":
                            text += f"пориви вітру до: {val} м/с\n"
                        case "clouds":
                            text += f"хмарність: {val} %\n"
                        case "uvi":
                            text += f"ультрафіолетове випромінювання: {val} \n"

                await message.answer(text)
    else:
        await message.answer("Дані не знайдено")
