# 모닥불 생성, 지연 삭제 필터링 조회가 포함된 쿼리

from typing import List, Optional
from schemas.topics import TopicCreate
from db.connection import get_db_connection
from datetime import datetime, timedelta, timezone
from core.exceptions import (
        TopicAlreadyExpiredException,
        TopicNotFoundException,
        TopicAlreadyExistsException,
 )

def create_topic(topic_data: TopicCreate, user_id: int) -> dict:
    """ 새로운 모닥불(Topic)을 피우고 DB에 저장합니다.

    생성 시점 기준으로 만료 일시(expires_at)를 현재 UTC 시간 + 1시간으로 자동 계산하여 부여합니다.

    Args:
        topic_data (TopicCreate): 모닥불의 본문(content)이 담긴 스키마
        user_id (int): 모닥불을 피우는 작성자의 고유 ID
    Returns:
        dict: DB에 방금 생성된 모닥불의 상세 정보 (id, expires_at 등 포함)
    """

    """
    TODO: [?] 모닥불 피우기
    1. INSERT INTO topics 로 데이터 삽입
    2. 삽입할 때 expires_at 값을 '현재 시간 + 1시간'으로 계산하여 넣기
    3. 방금 생성된 데이터(id 포함)를 SELECT 해서 리턴하기
    """

    # expires_at = now + 1 hour
    # timezone.utc, so the location of server won't matter
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # DB Connection
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if topic with similar content exists
        dup_query = """
            SELECT id FROM topics
            WHERE content = ?
                AND expires_at > datetime('now')
            LIMIT 1
        """
        cursor.execute(dup_query, (topic_data.content, ))
        if cursor.fetchone() is not None:
            raise TopicAlreadyExistsException()

        # INSERT
        #    id: AUTOINCREMENT
        #    comment_count: DEFAULT 0
        #    created_at: DEFAULT CURRENT_TIMESTAMP
        #
        # we need to put 'content, expires_at, user_id'
        insert_query = """
            INSERT INTO topics (content, expires_at, user_id)
            VALUES (?, ?, ?)
        """
        cursor.execute(insert_query, (topic_data.content, expires_at, user_id))

        # Last INSERTed row id
        new_topic_id = cursor.lastrowid

        # Commit changes
        conn.commit()

        select_query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(select_query, (new_topic_id,))
        row = cursor.fetchone()

    # Return slite3.Row object after converting to dict
    return dict(row)


def get_active_topics(limit: int = 20, offset: int = 0) -> List[dict]:
    """ 현재 살아있는 모닥불(Topic)의 피드 목록을 최신순으로 반환합니다.

    지연 삭제(Lazy Deletion) 로직이 적용되어, 이미 만료된 모닥불은 조회되지 않습니다.

    Args:
        limit (int): 한 번에 반환할 최대 모닥불의 개수 (기본값: 20)
        offset (int): DB에서 건너뛸 데이터의 개수 (페이징용. 예: 20이면 21번째 글부터 조회)

    Returns:
        List[dict]: 살아있는 모닥불들의 딕셔너리 리스트. (게시물이 없다면 빈 리스트[] 반환)

    """

    """
    TODO: [?] SYS-05 지연 삭제가 적용된 피드 목록
    1. SELECT * FROM topics WHERE expires_at > datetime('now') ORDER BY expires_at DESC LIMIT ? OFFSET ?
    2. 결과를 리스트로 묶어서 리턴
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # SELECT: (expires_at > current_time)
        query = """
            SELECT *
            FROM topics
            WHERE expires_at > datetime('now')
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (limit, offset))

        # fetchall (return emtpy list if nothing found)
        rows = cursor.fetchall()

    # Convert to dict
    # list comprehension:
    return [dict(row) for row in rows]


def get_topic_detail(topic_id: int) -> Optional[dict]:
    """ 특정 모닥불(Topic)에 대한 상세 정보를 반환합니다.

    해당 모닥불이 존재하더라도 이미 수명이 다했다면, 존재하지 않는 것과 동일하게 처리합니다.

    Args:
        topic_id (int): 조회할 특정 모닥불의 고유 ID

    Returns:
        dict: 특정 모닥불에 대한 상세 정보

    Raises:
        TopicNotFoundException: 해당 ID의 모닥불이 아예 존재하지 않을 경우 발생
        TopicAlreadyExpiredException: 모닥불이 존재하지만 이미 수명이 만료된 경우 발생

    """

    """
    TODO: [?] 모닥불 상세 조회
    1. SELECT * FROM topics WHERE id = ?
    2. 결과가 없으면 TopicNotFoundException() 던지기
    3. 결과가 있는데 expires_at이 현재 시간보다 과거라면 TopicAlreadyExpiredException() 던지기
    4. 유효하다면 딕셔너리 반환
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Find topic by ID
        topic_query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(topic_query, (topic_id, ))
        topic_row = cursor.fetchone()

        # If not found -> ERROR 404
        if topic_row is None:
            raise TopicNotFoundException()

        comment_query = """
            SELECT * FROM comments
            WHERE topic_id = ?
            ORDER BY created_at ASC
        """
        cursor.execute(comment_query, (topic_id, ))
        comment_rows = cursor.fetchall()

    # SQLite datetime ISO saved as string
    # Convert for comparison
    expires_at_str = topic_row["expires_at"]
    expires_at = datetime.fromisoformat(expires_at_str)
    now = datetime.now(timezone.utc)

    if expires_at < now:
        raise TopicAlreadyExpiredException()

    result = dict(topic_row)
    result["comments"] = [dict(row) for row in comment_rows]

    return result
