import requests
import json
from TelegramTextApp.utils.database import SQL_request
from TelegramTextApp.utils.utils import print_json
import TelegramTextApp
import os


def create_tokens():
    SQL_request("""
    CREATE TABLE IF NOT EXISTS github_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT,
        FOREIGN KEY (user_id) REFERENCES TTA(id)
    )""")


def get_token(tta_data):
    user_id = tta_data["id"]
    result = SQL_request(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='github_tokens';"
    )
    if not result:
        create_tokens()
    token_data = SQL_request(
        "SELECT * FROM github_tokens WHERE user_id=?", (user_id,), "one"
    )
    if token_data:
        return token_data["token"]
    else:
        return None


def fetch_github_data(url, tta_data):
    TOKEN = get_token(tta_data)
    if not TOKEN:
        return None
    headers = {"Authorization": f"token {TOKEN}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def gist_data(tta_data):
    try:
        gist_id = fetch_github_data("https://api.github.com/gists", tta_data)[
            int(tta_data["gist_id"])
        ]["id"]
        gist = fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)

        return {
            "gist_description": gist.get("description", ""),
            "gist_num_files": len(gist["files"]),
            "gist_updated_at": gist["updated_at"],
            "gist_forks_count": len(gist.get("forks", [])),
            "gist_comments": gist["comments"],
            "gist_created_at": gist["created_at"],
            "gist_owner": f"https://github.com/users/{gist['owner']['login']}",
        }
    except Exception as e:
        print(f"Возникла ошибка: {e}")
        return {"{gist_description}": f"GitHub API error: {str(e)}"}


def get_gists(tta_data):
    try:
        gists = fetch_github_data("https://api.github.com/gists", tta_data)
        data = {f"gist|{index}": g["description"] for index, g in enumerate(gists)}
        if not data:
            return {"none_gist": "А где?"}
        return data
    except:
        return {"add_token": "Добавить токен авторизации"}


def gist_files(tta_data):  # список файлов в гисте
    try:
        gist_index = tta_data["gist_id"]
        gist_id = fetch_github_data("https://api.github.com/gists", tta_data)[
            int(tta_data["gist_id"])
        ]["id"]
        gist = fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)
        return {
            f"gist_file|{gist_index}|{file['filename']}": file["filename"]
            for file in gist["files"].values()
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Ошибка при получении файлов: {str(e)}"}


def code_file(tta_data):  # содержимое файла из гиста
    try:
        gist_id = fetch_github_data("https://api.github.com/gists", tta_data)[
            int(tta_data["gist_id"])
        ]["id"]
        gist = fetch_github_data(f"https://api.github.com/gists/{gist_id}", tta_data)
        file_data = gist["files"].get(tta_data["gist_file"])
        if not file_data:
            return {"error": "Файл не найден в гисте"}
        return {"code": file_data["content"]}
    except Exception as e:
        print(f"Ошибка при открытии файла: {e}")
        return {"code": f"Ошибка при получении кода: {str(e)}"}


def save_token(tta_data):
    user_id = tta_data["id"]
    token = tta_data.get("github_token")
    if token:
        token_data = SQL_request(
            "SELECT * FROM github_tokens WHERE user_id=?", (user_id,), "one"
        )
        if token_data:
            SQL_request(
                "UPDATE github_tokens SET token = ? WHERE user_id = ?", (token, user_id)
            )
        else:
            SQL_request(
                "INSERT INTO github_tokens (user_id, token) VALUES (?, ?)",
                (user_id, token),
            )
            return
    else:
        return {"error_text": "Не верный токен"}


def get_user_token(tta_data):
    user_id = tta_data["id"]
    token = SQL_request(
        "SELECT token FROM github_tokens WHERE user_id=?", (user_id,), "one"
    )
    if not token:
        return {"token": "Токен не найден"}
    else:
        return {"token": f"`{token['token']}`"}


if __name__ == "__main__":
    TelegramTextApp.start()
