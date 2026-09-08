import json
import sqlite3
from config import DB_NAME, SYSTEM_PROMPT

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                user_id INTEGER PRIMARY KEY,
                messages TEXT NOT NULL
            )
        """)
        conn.commit()

def get_user_history(user_id: int) -> list:
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT messages FROM history WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return [SYSTEM_PROMPT]

def save_user_history(user_id: int, history: list):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        json_data = json.dumps(history, ensure_ascii=False)
        cursor.execute("""
            INSERT INTO history (user_id, messages) 
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET messages = excluded.messages
        """, (user_id, json_data))
        conn.commit()