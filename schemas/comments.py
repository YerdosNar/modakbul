# sqlite3 DB 연결 객체 반환 유틸리티

from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int | None = None
    topic_id: int