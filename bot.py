import requests
import json
from TelegramTextApp.database import SQL_request
import TelegramTextApp
import os
from dotenv import load_dotenv


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    print(f"Токен: {TOKEN}")
    DEBUG = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    TelegramTextApp.start(TOKEN, "bot.json", "database.db", debug=DEBUG)

async def create_tokens():
    # Пользователи
    await SQL_request('''
    CREATE TABLE IF NOT EXISTS github_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT,
        FOREIGN KEY (user_id) REFERENCES TTA(id)
    )''')

async def get_token(tta_data):
    user_id = tta_data["id"]
    result = await SQL_request("SELECT name FROM sqlite_master WHERE type='table' AND name='github_tokens';")
    if not result:
        await create_tokens()
    token_data = await SQL_request("SELECT * FROM github_tokens WHERE user_id=?", (user_id,), 'one')
    if token_data:
        return token_data["token"]
    else:
        return None


async def fetch_github_data(url, tta_data):
    TOKEN = await get_token(tta_data)
    if not TOKEN:
        return None

    """Выполняет запрос к GitHub API с авторизацией и возвращает JSON-данные."""
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Генерирует исключение для HTTP-ошибок
    return response.json()

async def gist_data(tta_data):
    """Получает метаданные гиста по его ID."""
    try:
        gist_id = tta_data["gist_id"]
        gist = await fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)
        
        return {
            "gist_description": gist.get("description", ""),
            "gist_num_files": len(gist["files"]),
            "gist_updated_at": gist["updated_at"],
            "gist_forks_count": len(gist.get("forks", [])),
            "gist_comments": gist["comments"],
            "gist_created_at": gist["created_at"],
            "gist_owner": f"https://github.com/users/{gist['owner']['login']}"
        }
    except:
        return {"error": f"GitHub API error: {str(e)}"}

async def get_gists(tta_data):
    """Получает гисты указанного пользователя (по умолчанию 'falbue')."""
    owner = tta_data.get("owner", "falbue")  # Поддержка кастомного владельца
    try:
        gists = await fetch_github_data(f"https://api.github.com/users/{owner}/gists", tta_data)
        return {f'gist|{g["id"]}': g["description"] for g in gists}
    except:
        return {"error": "Гисты не найдены"}

async def get_my_gists(tta_data):
    """НОВАЯ ФУНКЦИЯ: Получает гисты текущего пользователя по токену."""
    try:
        gists = await fetch_github_data("https://api.github.com/gists", tta_data)
        data = {f'gist|{g["id"]}': g["description"] for g in gists}
        if not data:
            return {"mini|none_gist": "А где?"}
        return data
    except:
        return {"add_token": "Добавить токен авторизации"}

async def gist_files(tta_data):
    """Получает список файлов в гисте."""
    try:
        gist_id = tta_data["gist_id"]
        gist = await fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)
        return {
            f'gist_file|{gist_id}|{file["filename"]}': file["filename"]
            for file in gist["files"].values()
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка при получении файлов: {str(e)}"}

async def code_file(tta_data):
    """Получает содержимое файла из гиста."""
    try:
        gist_id = tta_data["gist_id"]
        gist = await fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)
        file_data = gist["files"].get(tta_data["gist_file"])
        if not file_data:
            return {"error": "Файл не найден в гисте"}
        return {"code": file_data["content"]}
    except:
        return {"error": f"Ошибка при получении кода: {str(e)}"}

async def save_token(tta_data):
    user_id = tta_data["id"]
    token = tta_data.get("github_token")
    if token:
        token_data = await SQL_request("SELECT * FROM github_tokens WHERE user_id=?", (user_id,), 'one')
        if token_data:
            await SQL_request("UPDATE github_tokens SET token = ? WHERE user_id = ?", (token, user_id))
        else:
            await SQL_request('INSERT INTO github_tokens (user_id, token) VALUES (?, ?)', (user_id, token))
            return
    else:
        return {"error_text":"Не верный токен"}

async def get_token(tta_data):
    user_id = tta_data["id"]
    token = await SQL_request("SELECT token FROM github_tokens WHERE user_id=?", (user_id,), 'one')
    if not token:
        return {"token":"Токен не найден"}
    else:
        return {"token":f"`{token['token']}`"}