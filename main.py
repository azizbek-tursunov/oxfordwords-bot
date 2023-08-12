import asyncio
import datetime

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

import keyboards
import random
from config import BOT_TOKEN
from words import oxford_words

API_TOKEN = BOT_TOKEN

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_subscriptions = {}
user_preferences = {}


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Assalomu alaykum. Bu bot orqali siz 'Oxford 5000' dagi so'zlardan yodlab borishingiz mumkin",
                         reply_markup=keyboards.intro)


@dp.message_handler(text="So'z yodlashni boshlash")
async def subscribe(message: types.Message):
    await message.answer("Bir kunda nechta so'z yodlamoqchisiz?", reply_markup=keyboards.wordsCount)


@dp.message_handler(content_types="text")
async def get_words_count(message: types.Message):
    if message.text.isdigit():
        user_id = message.from_user.id
        user_subscriptions[user_id] = True
        user_preferences[user_id] = {'words_per_day': int(message.text), 'send_time': (12, 0)}
        await message.reply(f"Tayyor, Har kuni {message.text} tadan so'z o'rganamiz. \n"
                            f"Qachon o'rganishni boshlashni xohlaysiz?",
                            reply_markup=keyboards.time)
    else:
        user_id = message.from_user.id
        if user_id in user_preferences:
            await set_prefs_handler(message)


@dp.message_handler(lambda message: ':' in message.text)
async def set_prefs_handler(message: types.Message):
    user_id = message.from_user.id
    try:
        time_input = message.text
        hour, minute = map(int, time_input.split(':'))

        if 0 <= hour < 24 and 0 <= minute < 60:
            user_preferences[user_id]['send_time'] = (hour, minute)
            preferences = user_preferences.get(user_id)
            send_time = f"{preferences['send_time'][0]:02d}:{preferences['send_time'][1]:02d}"
            words_per_day = preferences['words_per_day']
            prefs_message = f"Sozlamalaringiz\nQabul qilish vaqti: {send_time}\nSo'zlar soni: {words_per_day}"
            await message.answer(prefs_message, reply_markup=types.ReplyKeyboardRemove())
    except (ValueError, IndexError):
        await message.reply("Iltimos qaytadan kiriting")


@dp.message_handler(commands=['stop'])
async def stop(message: types.Message):
    user_id = message.from_user.id
    user_subscriptions[user_id] = False
    await message.reply("Sizga yana kundalik so'zlar yuborilmaydi")


@dp.message_handler(text="Bekor qilish")
async def subscribe(message: types.Message):
    await message.answer("Bekor qilindi", reply_markup=types.ReplyKeyboardRemove())


async def send_daily_words():
    while True:
        await asyncio.sleep(60)  # Check every minute

        current_time = datetime.datetime.now().time()
        for user_id, subscribed in user_subscriptions.items():
            if subscribed and user_preferences[user_id]['send_time'] == (current_time.hour, current_time.minute):
                words_per_day = user_preferences[user_id]['words_per_day']
                random_words = random.sample(oxford_words, words_per_day)
                words_text = "\n".join(md.bold(word) for word in random_words)
                message = f"Here are your daily words:\n\n{words_text}"
                await bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_daily_words())
    dp.middleware.setup(LoggingMiddleware())
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
