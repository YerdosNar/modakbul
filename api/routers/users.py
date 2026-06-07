from fastapi import APIRouter, Query, status
from schemas.users import UserProfileResponse
import services.user_service as user_service

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK, summary="특정 사용자 프로필 및 최근 활동 조회")
def get_user_profile(
    user_id: int,
    limit: int = Query(5, ge=1, le=50, description="조회할 최근 모닥불/장작 목록 개수")
):
    """지정한 사용자의 프로필 기본 정보 및 최근 작성한 모닥불(Topic), 장작(Comment) 목록을 최신순으로 통합 조회합니다.

    이 엔드포인트는 공개 프로필 페이지 렌더링에 적합하며, 단 한 번의 호출로 프로필 요약 정보를 제공합니다.

    Args:
        user_id (int): 조회하고자 하는 대상 사용자의 고유 ID (URL Path)
        limit (int): 반환할 최근 모닥불 및 댓글의 최대 개수 (기본값 5, 1~50 범위)

    Returns:
        UserProfileResponse: 유저 정보 및 최근 활동 내역
    """
    return user_service.get_user_profile(user_id, limit)
