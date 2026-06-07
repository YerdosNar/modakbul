from core.time_utils import get_now, parse_iso
from schemas.comments import CommentCreate
from core.config import settings
from core.burn_rate import get_new_expires_at
from core.exceptions import TopicNotFoundException, TopicAlreadyExpiredException, DBIntegrityError, InvalidCommentContentException

import repositories.topic_repository as topic_repo
import repositories.comment_repository as comment_repo

# CRUD - Create

def create_comment(topic_id: int, comment_data: CommentCreate, user_id: int) -> dict:
    """시맨틱 밀도 감쇠 계수를 수식 연산하여 안전한 장작 투척(댓글 추가) 비즈니스 로직을 처리합니다.

    모닥불의 현재 만료 상태를 검증한 후, 유사 모닥불들의 장작 누적량에 비례해 
    산소 밀도 감쇠 계수(oxygen_factor)를 도출하고 이에 따른 새로운 수명 연장 만료일을 연산하여 댓글을 데이터베이스에 삽입합니다.

    Args:
        topic_id (int): 장작을 투척할 모닥불의 고유 ID.
        comment_data (CommentCreate): 삽입할 댓글 본문 데이터를 담은 객체.
        user_id (int): 댓글을 작성하는 인증된 사용자의 고유 ID.

    Returns:
        dict: 데이터베이스 적재가 완료되어 고유 번호 및 작성 시간이 부여된 댓글 상세 데이터.

    Raises:
        InvalidCommentContentException: 댓글 본문이 비어있거나 너무 길 때 발생합니다.
        TopicNotFoundException: 대상 모닥불을 찾을 수 없거나 데이터베이스 무결성 오류가 발생할 경우 발생합니다.
        TopicAlreadyExpiredException: 모닥불이 이미 재가 되었거나 수명이 만료되었을 때 발생합니다.
    """
    content = comment_data.content.strip() if comment_data.content else ""
    if not content or len(content) > settings.COMMENT_LENGTH_MAX:
        raise InvalidCommentContentException()

    topic = topic_repo.get_topic_by_id(topic_id)
    if topic is None:
        raise TopicNotFoundException()

    created_at = parse_iso(topic["created_at"])
    expires_at = parse_iso(topic["expires_at"])
    is_ash = topic["is_ash"]
    comment_count = topic["comment_count"]
    embedding_raw = topic["embedding"]

    now = get_now()
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

    try:
        return comment_repo.insert_comment_and_update_topic(
            topic_id=topic_id,
            content=content,
            user_id=user_id,
            now_iso=now.isoformat(),
            new_expires_iso=new_expires_at.isoformat()
        )
    except DBIntegrityError:
        raise TopicNotFoundException()


# CRUD - Read : 없음

# CRUD - Update : 없음

# CRUD - Delete : 없음