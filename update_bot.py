from aiogram import Bot
from logging_config import logger

async def update_bot_info(bot_token, data):
    bot = Bot(token=bot_token)
    new_name = data['name']
    new_short_description = data["short_description"]
    new_description = data["description"]
    try:
        # Получаем текущую информацию о боте
        me = await bot.get_me()
        bot_info = await bot.get_my_description()
        full_info = await bot.get_my_short_description()
        
        changes = {}
        
        # Проверка имени
        if new_name and new_name != me.full_name:
            changes["name"] = new_name
        
        # Проверка короткого описания
        if (
            new_short_description and 
            new_short_description != full_info.short_description
        ):
            changes["short_description"] = new_short_description
        
        # Проверка длинного описания
        if (
            new_description and 
            new_description != bot_info.description
        ):
            changes["description"] = new_description
        
        if not changes:
            logger.info("✅ Все данные актуальны. Изменения не требуются")
            return
        
        # Применяем изменения
        if "name" in changes:
            await bot.set_my_name(changes["name"])
        
        if "short_description" in changes:
            await bot.set_my_short_description(
                short_description=changes["short_description"]
            )
        
        if "description" in changes:
            await bot.set_my_description(
                description=changes["description"]
            )
            
        logger.info("\n✅ Все изменения применены")
        
    except Exception as e:
        logger.error(f"⛔ Ошибка: {e}")
    finally:
        await bot.session.close()