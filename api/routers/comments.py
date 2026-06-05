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
    return comment_service.create_comment(topic_id, comment_data, user_id)