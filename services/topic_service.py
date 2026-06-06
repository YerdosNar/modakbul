import json
from typing import List
from core.time_utils import get_now, get_now_iso, parse_iso, add_hours

from schemas.topics import TopicCreate
from core.config import settings
from core.embedding_utils import get_embedding
from core.similarity import calculate_cosine_similarity
from core.exceptions import TopicAlreadyExistsException, TopicNotFoundException, DBIntegrityError

import repositories.topic_repository as topic_repo
import repositories.comment_repository as comment_repo

# CRUD - Create

def create_new_topic(topic_data: TopicCreate, user_id: int) -> dict:
    """가상 시맨틱 임베딩 분석 및 모닥불 적재 비즈니스 로직을 통제합니다.

    신규 주제를 128차원 유닛 벡터로 변환한 후, 기존 활성 모닥불들과의 코사인 유사도를 연산합니다.
    유사도가 임계값 이상인 대상을 식별하여 경쟁 관계 테이블에 기록하며, 최종 생성된 모닥불 객체를 반환합니다.

    Args:
        topic_data (TopicCreate): 모닥불 생성을 위한 입력 데이터 객체 (주제 내용 포함).
        user_id (int): 모닥불을 생성하는 인증된 사용자의 고유 ID.

    Returns:
        dict: 데이터베이스 적재가 완료되어 식별 ID와 초기 수명이 부여된 모닥불 상세 데이터.

    Raises:
        TopicAlreadyExistsException: 활성 상태 중 동일한 내용의 모닥불이 이미 존재하거나 
                                     데이터베이스 무결성 오류가 발생할 경우 발생합니다.
    """
    now = get_now()
    now_iso = get_now_iso()
    expires_at_iso = add_hours(now, 1).isoformat()

    if topic_repo.check_active_topic_exists(topic_data.content, now_iso):
        raise TopicAlreadyExistsException()

    embedding_vector = get_embedding(topic_data.content)
    embedding_str = json.dumps(embedding_vector)

    try:
        new_topic_id = topic_repo.insert_topic(
            content=topic_data.content,
            expires_at=expires_at_iso,
            created_at=now_iso,
            user_id=user_id,
            embedding_str=embedding_str
        )

        active_topics = topic_repo.get_active_topics_with_embeddings(now_iso, new_topic_id)
        similarity_inserts = []
        for row in active_topics:
            try:
                other_vector = row["embedding"]
                if not other_vector:
                    continue
                similarity = calculate_cosine_similarity(embedding_vector, other_vector)

                if similarity >= settings.SIMILARITY_THRESHOLD:
                    similarity_inserts.append((row["id"], new_topic_id, similarity))
            except ValueError:
                continue

        if similarity_inserts:
            topic_repo.bulk_insert_topic_similarities(similarity_inserts)

    except DBIntegrityError:
        raise TopicAlreadyExistsException()

    return topic_repo.get_topic_by_id(new_topic_id)


# CRUD - Read

def read_topic_feed(limit: int = 20, offset: int = 0) -> List[dict]:
    """현재 활성 상태인 모닥불 목록만 슬라이싱하여 피드로 제공합니다.

    Args:
        limit (int, optional): 한 번에 조회할 최대 모닥불 개수. 기본값은 20.
        offset (int, optional): 건너뛸 오프셋 개수. 기본값은 0.

    Returns:
        List[dict]: 현재 살아있는 모닥불 목록을 담은 딕셔너리 리스트.
    """
    now_iso = get_now_iso()
    return topic_repo.get_active_topics_feed(now_iso, limit, offset)


def read_ash_topics_feed(limit: int = 20, offset: int = 0) -> List[dict]:
    """이미 수명이 다하여 재가 된 과거 모닥불 목록을 피드로 제공합니다.

    Args:
        limit (int, optional): 한 번에 조회할 최대 모닥불 개수. 기본값은 20.
        offset (int, optional): 건너뛸 오프셋 개수. 기본값은 0.

    Returns:
        List[dict]: 재가 된 과거 모닥불 목록을 담은 딕셔너리 리스트.
    """
    now_iso = get_now_iso()
    return topic_repo.get_combined_ash_topics_feed(now_iso, limit, offset)


def get_topic_detail(topic_id: int, limit: int = 20, offset: int = 0) -> dict:
    """물리보관(아카이브) 및 만료 시간 실시간 검증을 결합하여 고도화된 모닥불 상세 데이터를 가공합니다.

    활성 테이블과 아카이브 테이블 양쪽을 조회하여 모닥불 본문을 찾고, 
    해당 모닥불 하위에 달린 장작(댓글)들을 목록화하여 단일 응답 객체로 조합해 반환합니다.

    Args:
        topic_id (int): 상세 조회하고자 하는 모닥불의 고유 식별 번호.
        limit (int, optional): 하위 댓글을 조회할 페이징 크기 한도. 기본값은 20.
        offset (int, optional): 하위 댓글 페이징을 위한 오프셋. 기본값은 0.

    Returns:
        dict: 모닥불 상세 정보 및 댓글 목록(`comments`)이 결합된 딕셔너리.

    Raises:
        TopicNotFoundException: 해당 ID의 모닥불을 활성/아카이브 모두에서 찾을 수 없을 때 발생합니다.
    """
    is_archived = False
    topic_row = topic_repo.get_topic_by_id(topic_id)
    
    if topic_row is None:
        topic_row = topic_repo.get_ash_topic_by_id(topic_id)
        if topic_row is None:
            raise TopicNotFoundException()
        is_archived = True

    if is_archived:
        comment_rows = comment_repo.get_ash_comments_by_topic_id(topic_id, limit, offset)
    else:
        comment_rows = comment_repo.get_comments_by_topic_id(topic_id, limit, offset)

    result = dict(topic_row)

    if is_archived:
        result["is_ash"] = 1
    else:
        expires_at = parse_iso(result["expires_at"])
        if expires_at <= get_now():
            result["is_ash"] = 1

    result["comments"] = comment_rows
    return result


# CRUD - Update : 없음

# CRUD - Delete : 없음