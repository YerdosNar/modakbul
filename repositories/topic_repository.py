import sqlite3
from typing import List, Optional
from db.connection import get_db_connection

def check_active_topic_exists(content: str, now_iso: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id FROM topics
            WHERE content = ? AND expires_at > ? AND is_ash = 0
            LIMIT 1
        """
        cursor.execute(query, (content, now_iso))
        return cursor.fetchone() is not None

def insert_topic(content: str, expires_at: str, created_at: str, user_id: int, embedding_str: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO topics (content, expires_at, created_at, user_id, embedding, is_ash)
            VALUES (?, ?, ?, ?, ?, 0)
        """
        cursor.execute(query, (content, expires_at, created_at, user_id, embedding_str))
        conn.commit()
        return cursor.lastrowid

def get_active_topics_with_embeddings(now_iso: str, exclude_id: int) -> List[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, embedding FROM topics
            WHERE expires_at > ? AND is_ash = 0 AND id != ? AND embedding IS NOT NULL
        """
        cursor.execute(query, (now_iso, exclude_id))
        return [dict(row) for row in cursor.fetchall()]

def bulk_insert_topic_similarities(similarity_inserts: List[tuple]):
    if not similarity_inserts:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO topic_similarities (topic_id_1, topic_id_2, similarity)
            VALUES (?, ?, ?)
        """
        cursor.executemany(query, similarity_inserts)
        conn.commit()

def get_topic_by_id(topic_id: int) -> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(query, (topic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_ash_topic_by_id(topic_id: int) -> Optional[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM ash_topics WHERE id = ?"
        cursor.execute(query, (topic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_active_topics_feed(now_iso: str, limit: int, offset: int) -> List[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM topics
            WHERE expires_at > ? AND is_ash = 0
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (now_iso, limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_combined_ash_topics_feed(now_iso: str, limit: int, offset: int) -> List[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, content, expires_at, comment_count, is_ash, created_at, user_id FROM ash_topics
            UNION ALL
            SELECT id, content, expires_at, comment_count, is_ash, created_at, user_id FROM topics
            WHERE is_ash = 1 OR expires_at <= ?
            ORDER BY expires_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (now_iso, limit, offset))
        return [dict(row) for row in cursor.fetchall()]