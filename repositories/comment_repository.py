import sqlite3
from typing import List
from db.connection import get_db_connection
from core.exceptions import DBIntegrityError

# CRUD - Create

def insert_comment_and_update_topic(topic_id: int, content: str, user_id: int, now_iso: str, new_expires_iso: str) -> dict:
    """새로운 장작(댓글) 데이터를 삽입하고, 해당 모닥불의 만료 시간 및 댓글 카운트를 1 증가시킵니다.

    이 연산은 데이터 무결성을 위해 단일 트랜잭션 내에서 실행되며, 실패 시 롤백 처리됩니다.

    Args:
        topic_id (int): 댓글이 달릴 대상 모닥불의 고유 ID.
        content (str): 댓글 내용.
        user_id (int): 댓글을 작성하는 사용자의 고유 ID.
        now_iso (str): 댓글 작성 시각 (ISO format).
        new_expires_iso (str): 계산된 모닥불의 새로운 만료 시간 (ISO format).

    Returns:
        dict: 데이터베이스에 성공적으로 삽입된 댓글 데이터 정보 (id, content, created_at, user_id, topic_id).

    Raises:
        DBIntegrityError: 외래키 제약조건 위반(존재하지 않는 유저 또는 모닥불) 등의 무결성 에러 발생 시 던집니다.
        sqlite3.Error: 트랜잭션 제어 과정 중 기타 데이터베이스 오류 발생 시 발생합니다.
    """
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
            
        except sqlite3.IntegrityError as e:
            conn.rollback()
            raise DBIntegrityError(str(e))
        except Exception as e:
            conn.rollback()
            raise e


# CRUD - Read

def get_comments_by_topic_id(topic_id: int, limit: int, offset: int) -> List[dict]:
    """특정 모닥불 하위에 달린 활성 상태의 댓글 목록을 최신순으로 페이징 조회합니다.

    Args:
        topic_id (int): 조회하고자 하는 대상 모닥불의 고유 ID.
        limit (int): 한 번에 조회할 최대 댓글 개수 (페이징 제한).
        offset (int): 건너뛸 댓글 개수 (페이징 오프셋).

    Returns:
        List[dict]: 조회된 댓글 정보 딕셔너리들이 담긴 리스트.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
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
    """아카이브 테이블(ash_comments)에서 이미 재가 된 과거 특정 모닥불의 댓글 목록을 조회합니다.

    Args:
        topic_id (int): 조회하고자 하는 대상 과거 모닥불(ash_topic)의 고유 ID.
        limit (int): 한 번에 조회할 최대 댓글 개수.
        offset (int): 건너뛸 댓글 개수.

    Returns:
        List[dict]: 조회된 과거 댓글 정보 딕셔너리들이 담긴 리스트.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
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
    """시맨틱 산소 밀도(competition) 계산을 위해, 유사도가 임계값 이상인 주변 활성 모닥불들에 누적된 댓글의 총합을 구합니다.

    Args:
        now_iso (str): 다른 모닥불들의 만료 여부를 판별하기 위한 현재 시각 (ISO format).
        topic_id (int): 기준이 되는 모닥불의 고유 ID.
        threshold (float): 시맨틱 공간의 유사도를 판별할 코사인 유사도 기준 임계값.

    Returns:
        int: 임계값 이상의 유사도를 가진 주변 활성 모닥불들에 적재된 댓글의 총합 개수.

    Raises:
        sqlite3.Error: 데이터베이스 조회 및 조인 과정에서 오류가 발생할 경우 발생합니다.
    """
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


# CRUD - Update : 없음

# CRUD - Delete : 없음