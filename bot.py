from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

import asyncio

from dotenv import load_dotenv

from setup_menu import *

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
dp = Dispatcher()

# Обработчик команды
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