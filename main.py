import asyncio
import logging
import sys
import re

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardMarkup


from coord import get_coord
from weather_info import show_current_weather, show_forecast, show_forecast_by_date

# telegram token
TOKEN = "6361419585:AAFSJwZxG7WOp96PazxiibAt48J5STMmy3A"
# open weather token
API_KEY = "f7cb430e537fdb4174df8d87ac0d42e3"

dp = Dispatcher()
form_router = Router()


class States(StatesGroup):
    wait_city = State()
    wait_city_week = State()
    wait_city_date = State()
    wait_city_date_2 = State()
    wait_location = State()


# обробник команди start
@form_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:

    # клавіатура
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поточна погода за геолокацією 🌎"),
             KeyboardButton(text="Поточна погода за назвою міста 🏭🏢🏣🏢")],
            [KeyboardButton(text="Тижневий прогноз📰"),
             KeyboardButton(text="Прогноз погоди за назвою міста, на дату🗓")]
        ], resize_keyboard=True
    )

    # повідомлення та відображення клавіатури
    await message.answer("Виберіть дію або /help - для довідки", reply_markup=keyboard)


#  обробник команди help
@form_router.message(Command("help"))
async def command_start_handler(message: Message) -> None:

    await message.answer("1. Поточна погода за геолокацією\n"
                         " - функція працює лише на мобільних пристроях,\n"
                         " - для активації надішліть геомітку через 📎 телеграму\n\n"
                         "2. Поточна погода за назвою міста\n"
                         " - функція у якості аргумента приймає назву міста\n"
                         " - регістр вводу та мова не важливі\n\n"
                         "3. Тижневий прогноз\n"
                         " - функція у якості аргумента приймає назву міста\n"
                         " - регістр вводу та мова не важливі\n\n"
                         "4.Прогноз погоди за назвою міста, на дату\n"
                         " - функція послідовно запитує назву міста -> дату\n"
                         " - формат дати 2023-12-31\n"
                         "     \tрік - не нижче 2023\n"
                         "     \tмісяць - не більше 12\n"
                         "     \tдень не більше 31\n"
                         "     \tдень не далі ніж 8 діб від поточної дати\n\n"
                         "*****У разі не коректного вводу повтоно викличте бажану дію ⬇️")


@form_router.message(States.wait_location)
async def geo_handler(message: Message, state: FSMContext) -> None:
    """Обробляє введену геолокацію для отримання поточної погоди"""
    # отримуємо координати, довжину та широту
    try:
        coords = [message.location.latitude, message.location.longitude]
    except AttributeError:
        await message.answer("Дані геолокації не знайдені")
        await state.clear()
        coords = None

    if coords:
        await message.answer("Отримано локацію")
        # скидаємо стан на 0
        await state.clear()

        #  блок видачі інформації про погоду
        await show_current_weather(coords, API_KEY, message)


@form_router.message(States.wait_city)
async def sity_handler(message: Message, state: FSMContext) -> None:
    """Обробляє введену назву міста для отримання поточної погоди"""
    coords = await get_coord(message.text, API_KEY)
    if coords:
        #  блок видачі інформації про погоду
        await show_current_weather(coords, API_KEY, message)
    else:
        await message.answer("Не вірні дані")
    await state.clear()


@form_router.message(States.wait_city_week)
async def city_weeekly(message: Message, state: FSMContext):
    """Обробляє введену назву міста для отримання прогнозу на 8 діб"""
    coords = await get_coord(message.text, API_KEY)

    if coords:
        #  блок видачі інформації про погоду
        await show_forecast(coords, API_KEY, message)
    else:
        await message.answer("Не вірні дані")
    await state.clear()


@form_router.message(States.wait_city_date)
async def city_date(message: Message, state: FSMContext):
    """
    Перша ступінь обробника, для надсилання погоди за вказаною датою,
    отримує координати введеного користувачем міста від погодного api,
    у разі успішного отримання координат, перемикає стан та надає можливість
    відпрацювати ступені 2"""
    coords = await get_coord(message.text, API_KEY)
    if coords:

        # це збереження даних
        await state.update_data(wait_city_date=coords)

        #  перемикаємось у режим вводу дати
        await state.set_state(States.wait_city_date_2)
        await message.answer(
            "Введіть дату за форматом\n"
            "2023-12-31"
            )
    else:
        await message.answer("Місто не знайдено")
        await state.clear()


@form_router.message(States.wait_city_date_2)
async def city_date(message: Message, state: FSMContext):
    """
    Друга ступінь обробника, для надсилання погоди за вказаною датою,
    обробляє введення дати, та виконує її перевірку за регулярним виразом,
    у разі проходження перевірки надсилає прогноз за датою"""

    #  перевіряємо ввод за паттерном
    if re.match("^2023-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$", message.text):
        date = message.text

        # читання збережених даних зі стану
        coords = await state.get_data()

        if coords:
            #  блок видачі інформації про погоду
            await show_forecast_by_date(coords["wait_city_date"], API_KEY, message, date)

        else:
            await message.answer("Не вірні дані")
        await state.clear()

    else:
        await message.answer("Не вірний формат вводу")
    await state.clear()


# перемикач станів
@form_router.message(F.text)
async def switch(message: Message, state: FSMContext) -> None:
    """Залежно від тексту надісланого з кнопок перемикає стани"""
    if message.text == "Поточна погода за геолокацією 🌎":
        await state.set_state(States.wait_location)
        await message.answer("Надішліть геомітку 🗺:")

    elif message.text == "Поточна погода за назвою міста 🏭🏢🏣🏢":
        await state.set_state(States.wait_city)
        await message.answer("Надішліть назву міста:")

    elif message.text == "Тижневий прогноз📰":
        await state.set_state(States.wait_city_week)
        await message.answer("Надішліть назву міста:")

    elif message.text == "Прогноз погоди за назвою міста, на дату🗓":
        await state.set_state(States.wait_city_date)
        await message.answer("Надішліть назву міста:")


async def main() -> None:
    bot = Bot(TOKEN)
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
