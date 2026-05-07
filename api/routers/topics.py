# GET /topics, POST /topics 등

from typing import List
from fastapi import APIRouter, Depends, Query, status
from schemas.topics import TopicCreate, TopicResponse, TopicDetailResponse
from api.dependencies import get_current_user
import crud.topics

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post(
        "/",
        response_model=TopicResponse,
        status_code=status.HTTP_201_CREATED,
        summary="모닥불 피우기",
        description="새로운 주제의 모닥불(게시물)을 생성합니다. (로그인 필수)")
def create_new_topic(
    topic_data: TopicCreate,
    user_id: int = Depends(get_current_user)
):
    """새로운 모닥불을 DB에 생성합니다.

    생성된 모닥불은 기본적으로 현재 시간으로부터 1시간의 수명(expires_at)을 부여받습니다.

    Args:
        topic_data (TopicCreate): 모닥불의 제목과 내용이 담긴 객체
        user_id (int): Depends를 통해 주입된 현재 로그인 사용자의 고유 ID

    Returns:
        TopicResponse: 생성된 모닥불의 상세 정보 (id, expires_at 등 포함)
    """

    """
    TODO: [?] 모닥불 생성 로직 구현
    1. crud.topics.create_topic(topic_data, user_id 호출 후, 그 반환값을 그대로 리턴)
    """
    return crud.topics.create_topic(topic_data, user_id)


@router.get(
        "/",
        response_model=List[TopicResponse],
        summary="살아있는 모닥불 피드 조회")
def read_topic_feed(
    limit: int = Query(20, ge=1, le=100, description="한 번에 가져올 게시물 수"),
    offset: int = Query(0, ge=0, description="건너뛸 게시물 수 (페이징용)")
):
    """현재 살아있는(만료되지 않은) 모닥불 피드 목록을 최신순으로 조회합니다.

    지연 삭제(Lazy Deletion) 로직이 적용되어, 수명이 다한 모닥불은 목록에 노출되지 않습니다.
    Query 파라미터를 통해 무한 스크롤이나 페이징 처리를 지원합니다.

    Args:
        limit (int): 반환할 최대 게시물 수 (1~100 사이, 기본값 20)
        offset (int): 건너뛸 데이터의 개수 (기본값 0)

    Returns:
        List[TopicResponse]: 모닥불 정보가 담긴 리스트, 없으면 빈 리스트 반환.
    """

    """
    TODO: [?] 피드 조회 로직 구현
    1. crud.topics.get_active_topics(limit, offset) 호출 후, 그 반환값을 그대로 리턴
    """
    return crud.topics.get_active_topics(limit, offset)


@router.get(
        "/{topic_id}",
        response_model=TopicDetailResponse,
        summary="특정 모닥불 상세 조회")
def get_topic_detail(topic_id: int):
    """특정 모닥불의 상세 내용을 조회합니다.

    해당 ID의 모닥불이 존재하더라도 이미 수명이 다했다면 접근할 수 없습니다.

    Args:
        topic_id (int): 조회할 모닥불의 고유 ID (URL Path)

    Returns:
        TopicResponse: 해당 모닥불의 상세 정보

    Raises:
        TopicNotFoundExceptioin: (CRUD 내부 발생) 게시물이 아예 없을 때 404 반환
        TopicalreadyExpiredException: (CRUD 내부 발생) 게시물이 이미 만료되었을 때 403 반환
    """

    """
    TODO: [?] 모닥불 상세 조회 로직 구현
    1. crud.topics.get_topic_detail(topic_id) 호출 후, 그 반환값을 그대로 리턴
    (참고: 만료되거나 없는 게시물에 대한 404/403 에외 처리는 CRUD에서 던지므로 라우터에서는 호출만 하면 됨.)
    """
    return crud.topics.get_topic_detail(topic_id)
