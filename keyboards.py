from aiogram import types

intro = types.ReplyKeyboardMarkup(resize_keyboard=True)
intro.add(types.KeyboardButton("So'z yodlashni boshlash"))

wordsCount = types.ReplyKeyboardMarkup(resize_keyboard=True)
wordsCount.add(*[types.KeyboardButton(str(i)) for i in range(1, 11)])

time = types.ReplyKeyboardMarkup(resize_keyboard=True)
for hour in range(24):
    for minute in range(0, 60, 15):
        time.add(types.KeyboardButton(f"{hour:02d}:{minute:02d}"))

time.add(types.KeyboardButton("Bekor qilish"))