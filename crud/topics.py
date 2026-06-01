# 모닥불 생성, 지연 삭제 필터링 조회가 포함된 쿼리
import json
from typing import List, Optional
from schemas.topics import TopicCreate
from db.connection import get_db_connection
from datetime import datetime, timedelta, timezone
from core.exceptions import (
        TopicAlreadyExpiredException,
        TopicNotFoundException,
        TopicAlreadyExistsException,
 )
from core.embedding_utils import get_embedding
from core.config import settings
from core.similarity import calculate_cosine_similarity

def create_topic(topic_data: TopicCreate, user_id: int) -> dict:
    """ 새로운 모닥불(Topic)을 피우고 DB에 저장합니다.

    생성 시점 기준으로 만료 일시(expires_at)를 현재 UTC 시간 + 1시간으로 자동 계산하여 부여합니다.
    또한 본문(content)의 시맨틱 임베딩 벡터를 추출하여 JSON 문자열 형태로 함께 적재합니다.

    Args:
        topic_data (TopicCreate): 모닥불의 본문(content)이 담긴 스키마
        user_id (int): 모닥불을 피우는 작성자의 고유 ID

    Returns:
        dict: DB에 방금 생성된 모닥불의 상세 정보 (id, expires_at, embedding 등 포함)

    Raises:
        TopicAlreadyExistsException: 동일한 본문을 가진 활성 모닥불이 이미 존재할 경우 발생. 
    """

    # expires_at = now + 1 hour
    # timezone.utc, so the location of server won't matter
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    now_iso = datetime.now(timezone.utc).isoformat()
    

    # generate symantic virtual embedding vector and json string serialization.
    embedding_vector = get_embedding(topic_data.content)
    embedding_str = json.dumps(embedding_vector)

    # DB Connection
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Check if topic with similar content exists and is still active (is_ash = 0)
        dup_query = """
            SELECT id FROM topics
            WHERE content = ?
                AND expires_at > ?
                AND is_ash = 0
            LIMIT 1
        """
        cursor.execute(dup_query, (topic_data.content, now_iso))
        if cursor.fetchone() is not None:
            raise TopicAlreadyExistsException()

        # INSERT
        #    id: AUTOINCREMENT
        #    comment_count: DEFAULT 0
        #    created_at: DEFAULT CURRENT_TIMESTAMP
        #    embedding
        #    is_ash: DEFAULT 0
        #
        # we need to put 'content, expires_at, user_id'
        insert_query = """
            INSERT INTO topics (content, expires_at, created_at, user_id, embedding, is_ash)
            VALUES (?, ?, ?, ?, ?, 0)
        """
        cursor.execute(insert_query, (topic_data.content, expires_at, now_iso, user_id, embedding_str))

        # Last INSERTed row id
        new_topic_id = cursor.lastrowid

        # Fetch other active topics that have embeddings
        cursor.execute("""
            SELECT id, embedding FROM topics
            WHERE expires_at > ?
                AND is_ash = 0
                AND id != ?
                AND embedding IS NOT NULL
        """, (now_iso, new_topic_id))
        active_topics = cursor.fetchall()

        # Calculate cosine similarity with the new topic's embedding vector
        similarity_inserts = []
        for row in active_topics:
            try:
                other_vector = json.loads(row["embedding"])
                similarity = calculate_cosine_similarity(embedding_vector, other_vector)
                
                # Check against SIMILARITY_THRESHOLD from config settings
                if similarity >= settings.SIMILARITY_THRESHOLD:
                    # Enforce topic_id_1 < topic_id_2 for consistent symmetry
                    # Since new_topic_id is newly created, it is always greater than row["id"]
                    similarity_inserts.append((row["id"], new_topic_id, similarity))
            except (json.JSONDecodeError, ValueError):
                continue

        # Bulk insert into topic_similarities table if any matches found
        if similarity_inserts:
            cursor.executemany("""
                INSERT OR IGNORE INTO topic_similarities (topic_id_1, topic_id_2, similarity)
                VALUES (?, ?, ?)
            """, similarity_inserts)

        # Commit changes
        conn.commit()

        select_query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(select_query, (new_topic_id,))
        row = cursor.fetchone()

    # Return slite3.Row object after converting to dict
    return dict(row)


def get_active_topics(limit: int = 20, offset: int = 0) -> List[dict]:
    """ 현재 살아있는 모닥불(Topic)의 피드 목록을 최신순으로 반환합니다.

    지연 삭제(Lazy Deletion) 로직이 적용되어, 이미 만료되거나 재가 된 모닥불은 조회되지 않습니다.

    Args:
        limit (int): 한 번에 반환할 최대 모닥불의 개수 (기본값: 20)
        offset (int): DB에서 건너뛸 데이터의 개수 (페이징용. 예: 20이면 21번째 글부터 조회)

    Returns:
        List[dict]: 살아있는 모닥불들의 딕셔너리 리스트. (게시물이 없다면 빈 리스트[] 반환)

    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # SELECT: (expires_at > current_time AND is_ash = 0)
        query = """
            SELECT *
            FROM topics
            WHERE expires_at > ? AND is_ash = 0
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (now_iso, limit, offset))

        # fetchall (return emtpy list if nothing found)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]


def get_topic_detail(topic_id: int, limit: int = 20, offset: int = 0) -> Optional[dict]:
    """ 특정 모닥불(Topic)에 대한 상세 정보를 반환합니다.

    재(is_ash = 1)가 된 모닥불이거나 이미 아카이빙된 모닥불이더라도 조회가 가능합니다.
    식어가는 과정의 아카이브 감상을 보증하기 위해 상세 조회를 허용합니다.

    Args:
        topic_id (int): 조회할 특정 모닥불의 고유 ID

    Returns:
        dict: 특정 모닥불에 대한 상세 정보

    Raises:
        TopicNotFoundException: 해당 ID의 모닥불이 아예 존재하지 않을 경우 발생

    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 1. 활성 모닥불 테이블(topics)에서 먼저 조회 시도
        topic_query = "SELECT * FROM topics WHERE id = ?"
        cursor.execute(topic_query, (topic_id, ))
        topic_row = cursor.fetchone()

        is_archived = False
        if topic_row is None:
            # 2. 활성 테이블에 없으면 아카이브 테이블(ash_topics)에서 조회 시도
            topic_query = "SELECT * FROM ash_topics WHERE id = ?"
            cursor.execute(topic_query, (topic_id, ))
            topic_row = cursor.fetchone()
            if topic_row is None:
                raise TopicNotFoundException()
            is_archived = True

        # 3. 알맞은 댓글 테이블(comments 또는 ash_comments)에서 댓글 조회
        if is_archived:
            comment_query = """
                SELECT * FROM ash_comments
                WHERE topic_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
        else:
            comment_query = """
                SELECT * FROM comments
                WHERE topic_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
        cursor.execute(comment_query, (topic_id, limit, offset))
        comment_rows = cursor.fetchall()

    result = dict(topic_row)

    # 지연 삭제 및 아카이빙 판정 보정
    if is_archived:
        result["is_ash"] = 1
    else:
        expires_at = datetime.fromisoformat(result["expires_at"]).replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            result["is_ash"] = 1

    result["comments"] = [dict(row) for row in comment_rows]

    return result


def get_ash_topics(limit: int = 20, offset: int = 0) -> List[dict]:
    """ 수명이 다하여 '재(is_ash = 1)'가 된 과거의 모닥불 아카이브 피드를 반환합니다.

    가비지 컬렉터가 백그라운드 청크 단위로 이관 중일 때도 사용자 조회의 데이터 일관성을 위해,
    이미 아카이빙된 테이블(ash_topics)과 활성 테이블의 논리 잠금 상태(is_ash = 1) 모닥불을 함께 조회합니다.

    Args:
        limit (int): 한 번에 반환할 최대 모닥불의 개수 (기본값: 20)
        offset (int): DB에서 건너뛸 데이터의 개수 (페이징용. 예: 20이면 21번째 글부터 조회)

    Returns:
        List[dict]: 재가 된 모닥불들의 딕셔너리 리스트. (게시물이 없다면 빈 리스트[] 반환)
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # UNION ALL로 물리적 아카이브 테이블과 활성 테이블의 논리 잠금 상태를 함께 병합 조회
        query = """
            SELECT id, content, expires_at, comment_count, is_ash, created_at, user_id FROM ash_topics
            UNION ALL
            SELECT id, content, expires_at, comment_count, is_ash, created_at, user_id FROM topics
            WHERE is_ash = 1 OR expires_at <= ?
            ORDER BY expires_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, (now_iso, limit, offset))
        rows = cursor.fetchall()

    return [dict(row) for row in rows]