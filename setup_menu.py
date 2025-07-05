from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import json

from utils import *


def load_bot(level=''): # загрузка меню
    filename="bot.json"
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        data = data[level]
        return data

def create_keyboard(menu_data, format_data=None): # создание клавиатуры
    builder = InlineKeyboardBuilder()
    return_builder = InlineKeyboardBuilder()
    variable_buttons = load_bot("buttons")
    
    if "keyboard" in menu_data:
        if isinstance(menu_data["keyboard"], str):
            buttons_func = globals().get(menu_data["keyboard"])
            if buttons_func and callable(buttons_func):
                buttons_data = buttons_func()
                if isinstance(buttons_data, dict):
                    menu_data["keyboard"] = buttons_data
        
        if isinstance(menu_data["keyboard"], dict):
            rows = []  # Список для готовых строк кнопок
            current_row = []  # Текущая формируемая строка
            max_in_row = menu_data.get("row", 2)  # Максимум кнопок в строке
            
            for callback_data, button_text in menu_data["keyboard"].items():
                force_new_line = False
                if button_text.startswith('\\'):
                    button_text = button_text[1:]  # Удаляем символ переноса
                    force_new_line = True
                
                button_text = formatting_text(button_text, format_data)
                callback_data = formatting_text(callback_data, format_data)
                
                if callback_data.startswith("url:"): # Создаем кнопку
                    url = callback_data[4:]
                    button = InlineKeyboardButton(text=button_text, url=url)
                else:
                    button = InlineKeyboardButton(text=button_text, callback_data=callback_data)
                
                if len(current_row) >= max_in_row: # Проверяем необходимость завершения текущей строки
                    rows.append(current_row)
                    current_row = []
                
                if force_new_line and current_row: # Обрабатываем принудительный перенос
                    rows.append(current_row)
                    current_row = []
                
                current_row.append(button)
            
            if current_row: # Добавляем последнюю строку
                rows.append(current_row)
            
            for row in rows: # Собираем клавиатуру из подготовленных строк
                builder.row(*row)
    
    if "return" in menu_data: # Добавляем кнопку возврата если нужно
        return_builder.button(
            text=variable_buttons['return'],
            callback_data=f"return|{menu_data['return']}"
        )
        builder.row(*return_builder.buttons)  # Кнопка возврата всегда в новой строке
    
    return builder.as_markup()

def create_text(menu_data, template, format_data): # создание текста
    text = menu_data["text"]
    text = formatting_text(text, format_data)
    text = markdown(text)
    return text

def get_menu(callback):
    tta_data = {}
    try:
        menu_name = callback.data 
        message = callback.message
    except:
        print(callback)
        message = callback
        command = message.text
        commands = load_bot(level='commands')
        menu_name = commands.get(command.replace("/",""))
        if menu_name is None:
            return None

        tta_data["menu_name"] = menu_name.get("menu")
        tta_data["telegram_id"] = message.chat.id

    return get_menu(tta_data["menu_name"])

def create_menu(tta_data): # получение нужного меню
    menu_name = tta_data['menu_name']
    user = get_user(tta_data['telegram_id'])
    menus = load_bot(level='menu')
    menu_data = menus.get(menu_name.split("|")[0])
    template = menu_name

    if "|" in menu_name:
        prefix = menu_name.split("|")[0] + "|"
        
        for key in menus:
            if key.startswith(prefix):
                menu_data = (menus["menu"].get(key))
                template = key
                break

    format_data = parse_bot_data(template, menu_name)
    format_data["menu_name"] = menu_name

    if not menu_data:
        menu_data = menus.get("none_menu")

    text = create_text(menu_data, template, format_data)
    keyboard = create_keyboard(menu_data, format_data)
    
    return {"text":text, "keyboard":keyboard}