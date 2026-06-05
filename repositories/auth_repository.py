import sqlite3
from typing import Optional
from db.connection import get_db_connection

def exists_user_by_username_or_nickname(username: str, nickname: str) -> Optional[dict]:
    """username 또는 nickname으로 중복된 사용자가 있는지 조회합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT username, nickname FROM users WHERE username = ? OR nickname = ?"
        cursor.execute(query, (username, nickname))
        user = cursor.fetchone()
        return dict(user) if user else None

def create_user(username: str, hashed_password: str, nickname: str) -> dict:
    """새로운 유저 데이터를 테이블에 안전하게 삽입합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)"
        cursor.execute(query, (username, hashed_password, nickname))
        conn.commit()
        new_user_id = cursor.lastrowid
        
    return {
        "id": new_user_id,
        "username": username,
        "nickname": nickname
    }

def get_user_by_username(username: str) -> Optional[dict]:
    """로그인 자격 인증용 사용자 정보를 레코드에서 탐색합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, username, nickname, password_hash FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return dict(user) if user else None

def get_hashed_password_by_user_id(user_id: int) -> Optional[str]:
    """탈퇴 검증을 위해 사용자의 해시 비밀번호를 조회합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT password_hash FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result["password_hash"] if result else None

def delete_user_by_id(user_id: int) -> int:
    """유저 데이터를 레코드에서 영구 하드 딜리트 처리합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        return cursor.rowcount