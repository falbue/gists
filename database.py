import sqlite3

DB_PATH = "database.db"

def SQL_request(query, params=(), fetch='one', jsonify_result=False):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)

            if fetch == 'all':
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                result = [
                    {
                        col: json.loads(row[i]) if isinstance(row[i], str) and row[i].startswith('{') else row[i]
                        for i, col in enumerate(columns)
                    }
                    for row in rows
                ]

            elif fetch == 'one':
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    result = {
                        col: json.loads(row[i]) if isinstance(row[i], str) and row[i].startswith('{') else row[i]
                        for i, col in enumerate(columns)
                    }
                else:
                    result = None
            else:
                conn.commit()
                result = None

        except sqlite3.Error as e:
            print(f"Ошибка SQL: {e}")
            raise

    if jsonify_result and result is not None:
        return json.dumps(result, ensure_ascii=False, indent=2)
    return result


def create_tables():
    # Пользователи
    SQL_request('''
    CREATE TABLE IF NOT EXISTS TTA (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        first_name TEXT,
        last_name TEXT,
        username TEXT,
        message_id INTEGER,
        message_type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_approved BOOLEAN DEFAULT 1,
        role TEXT DEFAULT 'user'
    )''')

create_tables()

def create_user(bot_data):
    try: bot_data = bot_data.message
    except: pass

    try:
        telegram_id = bot_data.from_user.id
        first_name = bot_data.from_user.first_name
        last_name = bot_data.from_user.last_name if hasattr(bot_data.from_user, 'last_name') else None
        username = bot_data.from_user.username if hasattr(bot_data.from_user, 'username') else None
        message_id = bot_data.message_id
    
        SQL_request('''
        INSERT INTO TTA (
            telegram_id, 
            first_name, 
            last_name, 
            username, 
            message_id
        ) VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, first_name, last_name, username, message_id))

        return True
    except:
        return False
