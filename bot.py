from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import asyncio
import os
import json

import random
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

def load_menus(filename="local.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def get_menu(menu_name):
    menus = load_menus()
    menu_data = menus["menu"].get(menu_name)
    
    if not menu_data:
        raise ValueError(f"Menu '{menu_name}' not found")
    
    # Заменяем плейсхолдеры в тексте
    number = random.randint(1, 100)
    text = menu_data["text"]
    if "{number}" in text:
        number = random.randint(1, 100)
        text = text.format(number=number)
    
    builder = InlineKeyboardBuilder()
    return_builder = InlineKeyboardBuilder()
    
    # Добавляем основные кнопки
    if "buttons" in menu_data:
        for callback_data, button_text in menu_data["buttons"].items():
            if callback_data.startswith("url:"):
                url = callback_data[4:]
                builder.button(text=button_text, url=url)
            else:
                builder.button(text=button_text, callback_data=callback_data)

    builder.adjust(2)
    keyboard = builder.as_markup()
    # Добавляем кнопку возврата если есть
    if "return" in menu_data:
        return_builder.button(text="🔙 Назад", callback_data=f"return|{menu_data['return']}")
        keyboard.inline_keyboard.append(return_builder.as_markup().inline_keyboard[0])
    
    return text, keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    text, keyboard = get_menu("main")
    await message.answer(text, reply_markup=keyboard)

# Обработчики нажатий на кнопки
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.message.chat.id
    print(user_id, data)
    
    if data == "notification":
        await callback.answer("Это всплывающее уведомление!", show_alert=True)
        return
    
    elif data.split("|")[0] == "return":
        text, keyboard = get_menu(data.split("|")[1])

    else:
        text, keyboard = get_menu(data)
    
    await callback.message.edit_text(text=text, reply_markup=keyboard)
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())