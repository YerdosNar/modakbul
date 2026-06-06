from typing import List
from fastapi import APIRouter, Depends, Query, status
from schemas.topics import TopicCreate, TopicResponse, TopicDetailResponse
from api.dependencies import get_current_user
import services.topic_service as topic_service

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED, summary="모닥불 피우기")
def create_new_topic(topic_data: TopicCreate, user_id: int = Depends(get_current_user)):
    """새로운 모닥불을 DB에 생성합니다.

    생성된 모닥불은 기본적으로 현재 시간으로부터 1시간의 수명(expires_at)을 부여받습니다.

    Args:
        topic_data (TopicCreate): 모닥불의 제목과 내용이 담긴 객체
        user_id (int): Depends를 통해 주입된 현재 로그인 사용자의 고유 ID

    Returns:
        TopicResponse: 생성된 모닥불의 상세 정보 (id, expires_at 등 포함)
    """
    return topic_service.create_new_topic(topic_data, user_id)

@router.get("/", response_model=List[TopicResponse], summary="살아있는 모닥불 피드 조회")
def read_topic_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
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
    return topic_service.read_topic_feed(limit, offset)

@router.get("/ashes", response_model=List[TopicResponse], summary="꺼진 모닥불(재) 조회")
def get_ashes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """수명이 다하여 재(is_ash = 1) 상태가 된 식어버린 모닥불 피드를 최신순으로 조회합니다.

    Query 파라미터를 통해 무한 스크롤이나 페이징 처리를 지원합니다.

    Args:
        limit (int): 반환할 최대 게시물 수 (1~100 사이, 기본값 20)
        offset (int): 건너뛸 데이터의 개수 (기본값 0)

    Returns:
        List[TopicResponse]: 재가 된 모닥불 정보가 담긴 리스트, 없으면 빈 리스트 반환.
    """
    return topic_service.read_ash_topics_feed(limit, offset)

@router.get("/{topic_id}", response_model=TopicDetailResponse, summary="특정 모닥불 상세 조회")
def get_topic_detail(
    topic_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """특정 모닥불의 상세 내용을 조회합니다.

    해당 ID의 모닥불이 존재하더라도 이미 수명이 다했다면 접근할 수 없습니다.

    Args:
        topic_id (int): 조회할 모닥불의 고유 ID (URL Path)
        limit (int): 하위 댓글을 조회할 최대 개수 (기본값 20)
        offset (int): 건너뛸 댓글의 개수 (기본값 0)

    Returns:
        TopicDetailResponse: 해당 모닥불의 상세 정보 및 댓글 목록

    Raises:
        TopicNotFoundException: 해당 ID의 모닥불이 존재하지 않을 때 404 반환
    """
    return topic_service.get_topic_detail(topic_id, limit, offset)