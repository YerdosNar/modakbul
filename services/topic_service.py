import json
from typing import List
from datetime import datetime, timedelta, timezone

from schemas.topics import TopicCreate
from core.config import settings
from core.embedding_utils import get_embedding
from core.similarity import calculate_cosine_similarity
from core.exceptions import TopicAlreadyExistsException, TopicNotFoundException

import repositories.topic_repository as topic_repo
import repositories.comment_repository as comment_repo

def create_new_topic(topic_data: TopicCreate, user_id: int) -> dict:
    """가상 시맨틱 임베딩 분석 및 모닥불 적재를 통제합니다."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_at_iso = (now + timedelta(hours=1)).isoformat()

    if topic_repo.check_active_topic_exists(topic_data.content, now_iso):
        raise TopicAlreadyExistsException()

    embedding_vector = get_embedding(topic_data.content)
    embedding_str = json.dumps(embedding_vector)

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
            other_vector = json.loads(row["embedding"])
            similarity = calculate_cosine_similarity(embedding_vector, other_vector)

            if similarity >= settings.SIMILARITY_THRESHOLD:
                similarity_inserts.append((row["id"], new_topic_id, similarity))
        except (json.JSONDecodeError, ValueError):
            continue

    if similarity_inserts:
        topic_repo.bulk_insert_topic_similarities(similarity_inserts)

    return topic_repo.get_topic_by_id(new_topic_id)

def read_topic_feed(limit: int = 20, offset: int = 0) -> List[dict]:
    """활성 상태의 신선한 모닥불 목록만 슬라이싱하여 제공합니다."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return topic_repo.get_active_topics_feed(now_iso, limit, offset)

def read_ash_topics_feed(limit: int = 20, offset: int = 0) -> List[dict]:
    """재가 된 과거 모닥불 목록을 정합성을 통합하여 반환합니다."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return topic_repo.get_combined_ash_topics_feed(now_iso, limit, offset)

def get_topic_detail(topic_id: int, limit: int = 20, offset: int = 0) -> dict:
    """물리보관/지연삭제 보정을 결합한 고도화 상세 매핑 객체를 가공합니다."""
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
        expires_at = datetime.fromisoformat(result["expires_at"]).replace(tzinfo=timezone.utc)
        if expires_at <= datetime.now(timezone.utc):
            result["is_ash"] = 1

    result["comments"] = comment_rows
    return result