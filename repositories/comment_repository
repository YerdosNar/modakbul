import sqlite3
from typing import List
from db.connection import get_db_connection

def get_comments_by_topic_id(topic_id: int, limit: int, offset: int) -> List[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM comments
            WHERE topic_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (topic_id, limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_ash_comments_by_topic_id(topic_id: int, limit: int, offset: int) -> List[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT * FROM ash_comments
            WHERE topic_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (topic_id, limit, offset))
        return [dict(row) for row in cursor.fetchall()]

def get_near_active_comments_sum(now_iso: str, topic_id: int, threshold: float) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT COALESCE(SUM(t.comment_count), 0)
            FROM topics t
            WHERE t.expires_at > ?
                AND t.is_ash = 0
                AND t.id != ?
                AND t.id IN (
                    SELECT topic_id_2 FROM topic_similarities WHERE topic_id_1 = ? AND similarity >= ?
                    UNION
                    SELECT topic_id_1 FROM topic_similarities WHERE topic_id_2 = ? AND similarity >= ?
                )
        """
        cursor.execute(query, (now_iso, topic_id, topic_id, threshold, topic_id, threshold))
        row = cursor.fetchone()
        return row[0] if row else 0

def insert_comment_and_update_topic(topic_id: int, content: str, user_id: int, now_iso: str, new_expires_iso: str) -> dict:
    with get_db_connection() as conn:
        try:
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO comments (content, user_id, topic_id, created_at)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(insert_query, (content, user_id, topic_id, now_iso))
            comment_id = cursor.lastrowid

            update_query = """
                UPDATE topics
                SET expires_at = ?, comment_count = comment_count + 1
                WHERE id = ?
            """
            cursor.execute(update_query, (new_expires_iso, topic_id))
            
            conn.commit()
            
            select_query = "SELECT id, content, created_at, user_id, topic_id FROM comments WHERE id = ?"
            cursor.execute(select_query, (comment_id,))
            return dict(cursor.fetchone())
            
        except Exception as e:
            conn.rollback()
            raise e