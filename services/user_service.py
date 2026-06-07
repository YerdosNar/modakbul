from core.time_utils import get_now_iso
from core.exceptions import UserNotFoundException
import repositories.user_repository as user_repo

def get_user_profile(user_id: int, limit: int = 5) -> dict:
    """특정 유저의 정보와 최근 작성한 모닥불(Topic), 장작(Comment) 목록을 종합하여 반환합니다.

    Args:
        user_id (int): 조회할 유저의 고유 ID.
        limit (int, optional): 최근 활동 목록을 조회할 개수 한도. 기본값은 5.

    Returns:
        dict: 유저 기본 정보 및 최근 활동 내역(recent_topics, recent_comments)이 결합된 딕셔너리.

    Raises:
        UserNotFoundException: 해당 ID의 사용자가 존재하지 않을 경우 발생합니다.
    """
    user_info = user_repo.get_user_profile_info(user_id)
    if user_info is None:
        raise UserNotFoundException()

    now_iso = get_now_iso()
    recent_topics = user_repo.get_recent_topics_by_user_id(user_id, limit, now_iso)
    recent_comments = user_repo.get_recent_comments_by_user_id(user_id, limit, now_iso)

    return {
        "user": user_info,
        "recent_topics": recent_topics,
        "recent_comments": recent_comments
    }
