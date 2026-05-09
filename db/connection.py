# sqlite3 DB 연결 객체 반환 유틸리티

import sqlite3
from contextlib import contextmanager
from core.exceptions import ResourceAccessError

DB_FILENAME = "modakbul.db"

@contextmanager
def get_db_connection():
    """
    DB connection을 생성하고 관리하는 유틸리티입니다.
    사용법 : with get_db_connection() as conn:
    """
    conn = sqlite3.connect(DB_FILENAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def check_db_connection(db_url: str):
    try:
        # sqlite:///./modakbul.db에서 경로만 추출
        db_path = db_url.replace("sqlite:///", "")
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        raise ResourceAccessError(f"DB 연결 실패: {str(e)}")