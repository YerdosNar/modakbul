from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import UserCreate, UserDelete, TokenResponse
import services.auth_service as auth_service
from core.security import create_access_token
from api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED, summary="회원가입")
def signup(user_data: UserCreate):
    new_user = auth_service.create_user(user_data.username, user_data.password, user_data.nickname)
    return {
        "message" : "회원가입이 완료되었습니다.",
        "user": new_user
    }

@router.post("/login", response_model=TokenResponse, summary="로그인 및 토큰 발급")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_service.authenticate_user(username=form_data.username, password=form_data.password)
    token_data = {"sub": str(user["id"])}
    access_token = create_access_token(data=token_data)
    return {
        "access_token": access_token,
        "token_type" : "bearer"
    }

@router.post("/logout", summary="로그아웃 및 토큰 삭제 유도 응답")
def logout():
    return {"message" : "로그아웃 되었습니다."}

@router.delete("/me", response_model=dict, summary="현재 로그인한 사용자 삭제")
def withdraw(user_data: UserDelete, current_user_id: int = Depends(get_current_user)):
    auth_service.delete_user(user_data.password, current_user_id)
    return {"message" : "회원 탈퇴가 완료되었습니다."}
    
@router.get("/me", summary="현재 로그인한 사용자 정보 조회")
def read_users_me(current_user_id: int = Depends(get_current_user)):
    return {
        "message": "인증 통과",
        "user_id": current_user_id
    }