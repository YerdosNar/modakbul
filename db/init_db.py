# CREATE TABLE 쿼리를 모아둔 초기화 스크립트

import sqlite3
import os
from core.config import settings

# USERNAME_LENGTH_MAX = 31
# NICKNAME_LENGTH_MAX = 31
# TOPIC_LENGTH_MAX = 127
# COMMENT_LENGTH_MAX = 1023

def init_db():
    """ Initialize Database Table and Index. """
    path = os.path.dirname(os.path.abspath(__file__))
    print(path)
    os.makedirs(path, exist_ok=True)

    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()

    # 1. [Users] Table 
    query = f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR({settings.USERNAME_LENGTH_MAX}) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            nickname VARCHAR({settings.NICKNAME_LENGTH_MAX}) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    cursor.execute(query)
    
    # 2. [Topics] Table
    query = f"""
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content VARCHAR({settings.TOPIC_LENGTH_MAX}) NOT NULL,
            expires_at DATETIME NOT NULL,
            comment_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
        )
    """
    cursor.execute(query)

    
    # [Comments] Table
    query = f"""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content VARCHAR({settings.COMMENT_LENGTH_MAX}) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            topic_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
            FOREIGN KEY (topic_id) REFERENCES topics (id) ON DELETE CASCADE
        )
    """
    cursor.execute(query)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__name__":
    print("A")
    init_db()