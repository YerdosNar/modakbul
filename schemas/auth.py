# 회원가입 입력/출력 폼

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    nickname: str

class UserDelete(BaseModel):
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

