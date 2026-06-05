from datetime import datetime, timezone
from schemas.comments import CommentCreate
from core.config import settings
from core.burn_rate import get_new_expires_at
from core.exceptions import TopicNotFoundException, TopicAlreadyExpiredException

import repositories.topic_repository as topic_repo
import repositories.comment_repository as comment_repo

def create_comment(topic_id: int, comment_data: CommentCreate, user_id: int) -> dict:
    """시맨틱 밀도 감쇠 계수를 수식 연산하여 안전한 장작 투척을 지시합니다."""
    topic = topic_repo.get_topic_by_id(topic_id)
    if topic is None:
        raise TopicNotFoundException()

    created_at = datetime.fromisoformat(topic["created_at"]).replace(tzinfo=timezone.utc)
    expires_at = datetime.fromisoformat(topic["expires_at"]).replace(tzinfo=timezone.utc)
    is_ash = topic["is_ash"]
    comment_count = topic["comment_count"]
    embedding_raw = topic["embedding"]

    now = datetime.now(timezone.utc)
    if is_ash == 1 or expires_at <= now:
        raise TopicAlreadyExpiredException()

    near_comments_sum = 0
    if embedding_raw:
        try:
            near_comments_sum = comment_repo.get_near_active_comments_sum(
                now_iso=now.isoformat(),
                topic_id=topic_id,
                threshold=settings.SIMILARITY_THRESHOLD
            )
        except Exception:
            pass

    oxygen_factor = max(0.3, 1.0 - (near_comments_sum * 0.05))
    new_expires_at = get_new_expires_at(created_at, expires_at, comment_count, oxygen_factor)

    return comment_repo.insert_comment_and_update_topic(
        topic_id=topic_id,
        content=comment_data.content,
        user_id=user_id,
        now_iso=now.isoformat(),
        new_expires_iso=new_expires_at.isoformat()
    )