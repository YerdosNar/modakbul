# 모닥불 생성 입력/출력 폼

from pydantic import BaseModel
from datetime import datetime
from typing   import List
from schemas.comments import CommentResponse

class TopicCreate(BaseModel):
    content: str

class TopicResponse(BaseModel):
    id: int
    content: str
    expires_at: datetime
    comment_count: int
    created_at: datetime
    user_id: int

class TopicDetailResponse(TopicResponse):
    comments: List[CommentResponse]
