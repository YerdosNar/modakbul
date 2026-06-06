from fastapi import APIRouter, Depends, status
from schemas.comments import CommentCreate, CommentResponse
from api.dependencies import get_current_user
import services.comment_service as comment_service

router = APIRouter(prefix="/topics", tags=["Comments"])

@router.post("/{topic_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED, summary="장작(댓글) 추가 및 모닥불 수명 연장")
def add_comment_to_topic(
    topic_id: int,
    comment_data: CommentCreate,
    user_id: int = Depends(get_current_user)
):
    """살아있는 모닥불에 장작(댓글)을 추가하여 수명을 연장합니다.

    JWT 토큰을 통해 인증된 사용자만 접근할 수 있습니다.
    장작이 추가되면 백엔드(CRUD) 트랜잭션 내부에서 가변 연소율 알고리즘에 따라
    해당 모닥불의 만료 시간(expires_at)을 자동으로 연장합니다.

    Args:
        topic_id (int): 장작을 넣을 대상 모닥불의 고유 ID (URL Path)
        comment_data (CommentCreate): 추가할 장작의 본문 내용이 담긴 객체 (Request Body)
        user_id (int): 현재 로그인한 사용자의 고유 ID (Depends 미들웨어에서 자동 주입)

    Returns:
        CommentResponse: 성공적으로 DB에 저장된 장작의 상세 정보

    Raises:
        TopicNotFoundException: (CRUD 내부 발생) 해당 ID의 모닥불이 아예 없을 때 404 반환
        TopicAlreadyExpiredException: (CRUD 내부 발생) 모닥불이 이미 수명을 다했을 때 403 반환
    """
    return comment_service.create_comment(topic_id, comment_data, user_id)