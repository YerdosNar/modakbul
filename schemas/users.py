# 유저 프로필 조회 입력/출력 폼

from pydantic import BaseModel
from datetime import datetime
from typing import List
from schemas.topics import TopicResponse

class UserProfileInfo(BaseModel):
    id: int
    username: str
    nickname: str
    created_at: datetime

class TopicBriefInfo(BaseModel):
    id: int
    content: str
    is_ash: int

class CommentWithTopicResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    topic: TopicBriefInfo

class UserProfileResponse(BaseModel):
    user: UserProfileInfo
    recent_topics: List[TopicResponse]
    recent_comments: List[CommentWithTopicResponse]
