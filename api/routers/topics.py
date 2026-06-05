from typing import List
from fastapi import APIRouter, Depends, Query, status
from schemas.topics import TopicCreate, TopicResponse, TopicDetailResponse
from api.dependencies import get_current_user
import services.topic_service as topic_service

router = APIRouter(prefix="/topics", tags=["Topics"])

@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED, summary="모닥불 피우기")
def create_new_topic(topic_data: TopicCreate, user_id: int = Depends(get_current_user)):
    return topic_service.create_new_topic(topic_data, user_id)

@router.get("/", response_model=List[TopicResponse], summary="살아있는 모닥불 피드 조회")
def read_topic_feed(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return topic_service.read_topic_feed(limit, offset)

@router.get("/ashes", response_model=List[TopicResponse], summary="꺼진 모닥불(재) 조회")
def get_ashes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return topic_service.read_ash_topics_feed(limit, offset)

@router.get("/{topic_id}", response_model=TopicDetailResponse, summary="특정 모닥불 상세 조회")
def get_topic_detail(
    topic_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return topic_service.get_topic_detail(topic_id, limit, offset)