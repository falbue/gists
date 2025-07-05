from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

import asyncio

from setup_menu import *

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
dp = Dispatcher()

# Обработчик команды
@dp.message()
async def start_command(message: types.Message):
    if message.text[0] == "/":
        user_id = message.chat.id
        logger.debug(f"id: {user_id} | Команда: {message.text}")
        menu = await get_menu(message)

        if menu is None:
            await message.delete()
        else:
            await message.answer(menu["text"], reply_markup=menu["keyboard"])

# Обработчики нажатий на кнопки
@dp.callback_query()
async def handle_callback(callback: types.CallbackQuery):
    data = callback.data
    user_id = callback.message.chat.id
    logger.debug(f"id: {user_id} | Кнопка: {data}")
    
    if data == "notification":
        await callback.answer("Это всплывающее уведомление!", show_alert=True)
        return

    else:
        menu = await get_menu(callback)
    
    await callback.message.edit_text(menu["text"], reply_markup=menu["keyboard"])
    await callback.answer()

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Бот запущен")
    asyncio.run(main())