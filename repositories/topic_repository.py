import sqlite3
import json
from typing import List, Optional
from db.connection import get_db_connection
from core.exceptions import DBIntegrityError

# CRUD - Create

def insert_topic(content: str, expires_at: str, created_at: str, user_id: int, embedding_str: str) -> int:
    """새로운 모닥불(Topic) 데이터를 테이블에 안전하게 삽입합니다.

    Args:
        content (str): 등록할 모닥불의 주제/내용.
        expires_at (str): 모닥불의 만료 시간 (ISO format).
        created_at (str): 모닥불이 처음 생성된 시간 (ISO format).
        user_id (int): 모닥불을 생성한 사용자의 고유 ID.
        embedding_str (str): 모닥불 내용에서 추출한 128차원 유닛 벡터의 JSON 문자열.

    Returns:
        int: 새로 삽입된 모닥불의 고유 식별 번호 (lastrowid).

    Raises:
        DBIntegrityError: 고유 제약조건 위반 또는 외래키 제약조건 위반 시 발생합니다.
        sqlite3.Error: 데이터베이스 삽입 과정에서 데이터베이스 관련 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT INTO topics (content, expires_at, created_at, user_id, embedding, is_ash)
            VALUES (?, ?, ?, ?, ?, 0)
        """
        try:
            cursor.execute(query, (content, expires_at, created_at, user_id, embedding_str))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            raise DBIntegrityError(str(e))


def bulk_insert_topic_similarities(similarity_inserts: List[tuple]) -> None:
    """새로 생성된 모닥불과 기존 활성 모닥불들 간의 유사도 기록 리스트를 일괄 삽입합니다.

    Args:
        similarity_inserts (List[tuple]): (topic_id_1, topic_id_2, similarity)로 구성된 튜플들의 리스트.

    Returns:
        None

    Raises:
        DBIntegrityError: 제약조건 위반 시 발생합니다.
        sqlite3.Error: 일괄 데이터 삽입 과정에서 오류가 발생할 경우 발생합니다.
    """
    if not similarity_inserts:
        return
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            INSERT OR IGNORE INTO topic_similarities (topic_id_1, topic_id_2, similarity)
            VALUES (?, ?, ?)
        """
        try:
            cursor.executemany(query, similarity_inserts)
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise DBIntegrityError(str(e))


# CRUD - Read

def check_active_topic_exists(content: str, now_iso: str) -> bool:
    """동일한 내용의 활성화된 모닥불이 이미 존재하는지 확인합니다.

    Args:
        content (str): 중복 검사를 진행할 모닥불의 주제/내용.
        now_iso (str): 만료 여부를 판별하기 위한 현재 시각 (ISO format).

    Returns:
        bool: 동일 내용의 활성 상태 모닥불이 존재할 경우 True, 그렇지 않으면 False를 반환합니다.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id FROM topics
            WHERE content = ? AND expires_at > ? AND is_ash = 0
            LIMIT 1
        """
        cursor.execute(query, (content, now_iso))
        return cursor.fetchone() is not None


def get_active_topics_with_embeddings(now_iso: str, exclude_id: int) -> List[dict]:
    """유사도 계산을 위해, 특정 모닥불을 제외한 현재 활성 상태의 모닥불들의 ID와 임베딩 정보를 조회합니다.

    Args:
        now_iso (str): 활성 상태 판별을 위한 현재 시각 (ISO format).
        exclude_id (int): 유사도 비교 대상에서 제외할 신규 모닥불의 고유 ID.

    Returns:
        List[dict]: 각 모닥불의 정보가 담긴 딕셔너리 리스트. 
                    (embedding 필드는 json.loads를 거쳐 파이썬 List[float] 객체로 변환되어 전달됩니다.)

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT id, embedding FROM topics
            WHERE expires_at > ? AND is_ash = 0 AND id != ? AND embedding IS NOT NULL
        """
        cursor.execute(query, (now_iso, exclude_id))
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            row_dict = dict(row)
            try:
                row_dict["embedding"] = json.loads(row_dict["embedding"]) if row_dict["embedding"] else None
            except (json.JSONDecodeError, TypeError):
                row_dict["embedding"] = None
            result.append(row_dict)
        return result


def get_topic_by_id(topic_id: int) -> Optional[dict]:
    """활성 모닥불 테이블(topics)에서 특정 ID의 모닥불 상세 정보를 단건 조회합니다.

    Args:
        topic_id (int): 조회할 모닥불의 고유 식별 번호.

    Returns:
        Optional[dict]: 조회된 모닥불 정보 딕셔너리, 존재하지 않을 경우 None을 반환합니다.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(query, (topic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_ash_topic_by_id(topic_id: int) -> Optional[dict]:
    """아카이브 테이블(ash_topics)에서 이미 재가 된 특정 ID의 과거 모닥불 정보를 단건 조회합니다.

    Args:
        topic_id (int): 조회할 아카이브 모닥불의 고유 식별 번호.

    Returns:
        Optional[dict]: 조회된 과거 모닥불 정보 딕셔너리, 존재하지 않을 경우 None을 반환합니다.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM ash_topics WHERE id = ?"
        cursor.execute(query, (topic_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_active_topics_feed(now_iso: str, limit: int, offset: int) -> List[dict]:
    """현재 활활 타오르는(만료되지 않은) 모닥불 목록을 최신 생성순으로 슬라이싱하여 조회합니다.

    Args:
        now_iso (str): 활성 상태 판별을 위한 현재 시각 (ISO format).
        limit (int): 반환할 최대 레코드 수 (페이징 한도).
        offset (int): 건너뛸 레코드 수 (페이징 오프셋).

    Returns:
        List[dict]: 활성 모닥불 정보 딕셔너리들이 담긴 리스트.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 오류가 발생할 경우 발생합니다.
    """
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
    """이미 재가 되었거나 만료 예정 시각이 지난 과거 모닥불 목록을 정합하여 최신 만료순으로 조회합니다.

    Args:
        now_iso (str): 만료 여부를 실시간으로 대조하기 위한 현재 시각 (ISO format).
        limit (int): 반환할 최대 레코드 수 (페이징 한도).
        offset (int): 건너뛸 레코드 수 (페이징 오프셋).

    Returns:
        List[dict]: 아카이브된 과거 모닥불들의 정보 딕셔너리가 담긴 리스트.

    Raises:
        sqlite3.Error: 데이터베이스 조회 및 결합 과정에서 오류가 발생할 경우 발생합니다.
    """
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


# CRUD - Update : 없음

# CRUD - Delete : 없음