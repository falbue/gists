from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import json

from utils import *


def load_menus(filename="local.json"): # загрузка меню
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def create_keyboard(menu_data, format_data=None):
    builder = InlineKeyboardBuilder()
    return_builder = InlineKeyboardBuilder()
    
    # Обработка buttons, если это строка (название функции)
    if "buttons" in menu_data:
        if isinstance(menu_data["buttons"], str):
            # Получаем функцию по имени и вызываем её
            buttons_func = globals().get(menu_data["buttons"])
            if buttons_func and callable(buttons_func):
                buttons_data = buttons_func()
                if isinstance(buttons_data, dict):
                    menu_data["buttons"] = buttons_data
        
        # Добавляем основные кнопки (теперь buttons точно словарь)
        if isinstance(menu_data["buttons"], dict):
            for callback_data, button_text in menu_data["buttons"].items():
                button_text = formatting_text(button_text, format_data)
                callback_data = formatting_text(callback_data, format_data)
                if callback_data.startswith("url:"):
                    url = callback_data[4:]
                    builder.button(text=button_text, url=url)
                else:
                    builder.button(text=button_text, callback_data=callback_data)

    builder.adjust(2)
    keyboard = builder.as_markup()
    
    if "return" in menu_data:   # Добавляем кнопку возврата если есть
        return_builder.button(text="🔙 Назад", callback_data=f"return|{menu_data['return']}")
        keyboard.inline_keyboard.append(return_builder.as_markup().inline_keyboard[0])

    return keyboard

def get_menu(menu_name): # получение нужного меню
    menus = load_menus()
    menu_data = menus["menu"].get(menu_name.split("|")[0])
    template = menu_name

    if "|" in menu_name:
        prefix = menu_name.split("|")[0] + "|"
        
        for key in menus["menu"]:
            if key.startswith(prefix):
                menu_data = (menus["menu"].get(key))
                template = key
                break


    
    if not menu_data:
        menu_data = menus["menu"].get("none_menu")

    text = menu_data["text"]
    format_data = parse_bot_data(template, menu_name)
    format_data["menu_name"] = menu_name
    text = formatting_text(text, format_data)
    text = markdown(text)
    
    keyboard = create_keyboard(menu_data, format_data)
    
    return text, keyboard