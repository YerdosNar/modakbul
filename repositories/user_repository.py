import sqlite3
from typing import List, Optional
from db.connection import get_db_connection

def get_user_profile_info(user_id: int) -> Optional[dict]:
    """유저 테이블에서 특정 유저의 프로필 기본 정보를 단건 조회합니다."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, username, nickname, created_at FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_recent_topics_by_user_id(user_id: int, limit: int, now_iso: str) -> List[dict]:
    """특정 유저가 작성한 모닥불(Topic) 중 살아있는(만료되지 않은) 목록만 최신순으로 조회합니다.

    법적 아카이브용 테이블(ash_topics)은 조회 대상에서 완전히 제외됩니다.

    Args:
        user_id (int): 작성자의 고유 식별 번호.
        limit (int): 반환할 최대 레코드 수.
        now_iso (str): 만료 여부를 판별하기 위한 현재 시각 (ISO format).

    Returns:
        List[dict]: 만료되지 않은 최신순 모닥불 정보 딕셔너리 리스트.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, content, expires_at, comment_count, created_at, user_id, is_ash
            FROM topics
            WHERE user_id = ? AND expires_at > ? AND is_ash = 0
            ORDER BY created_at DESC
            LIMIT ?
        """
        cursor.execute(query, (user_id, now_iso, limit))
        return [dict(row) for row in cursor.fetchall()]


def get_recent_comments_by_user_id(user_id: int, limit: int, now_iso: str) -> List[dict]:
    """특정 유저가 작성한 장작(Comment) 중 모닥불이 살아있는 목록과 해당 모닥불 정보를 최신순으로 조회합니다.

    법적 아카이브용 테이블(ash_comments)은 조회 대상에서 완전히 제외됩니다.

    Args:
        user_id (int): 작성자의 고유 식별 번호.
        limit (int): 반환할 최대 레코드 수.
        now_iso (str): 원본 모닥불의 만료 여부를 판별하기 위한 현재 시각 (ISO format).

    Returns:
        List[dict]: 만료되지 않은 댓글 정보 및 원본 모닥불 요약 정보 리스트.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT c.id, c.content, c.created_at, c.topic_id,
                   t.content AS topic_content,
                   t.is_ash AS topic_is_ash
            FROM comments c
            JOIN topics t ON c.topic_id = t.id
            WHERE c.user_id = ? AND t.expires_at > ? AND t.is_ash = 0
            ORDER BY c.created_at DESC
            LIMIT ?
        """
        cursor.execute(query, (user_id, now_iso, limit))
        
        result = []
        for row in cursor.fetchall():
            row_dict = dict(row)
            result.append({
                "id": row_dict["id"],
                "content": row_dict["content"],
                "created_at": row_dict["created_at"],
                "topic_id": row_dict["topic_id"],
                "topic": {
                    "id": row_dict["topic_id"],
                    "content": row_dict["topic_content"],
                    "is_ash": row_dict["topic_is_ash"]
                }
            })
        return result
