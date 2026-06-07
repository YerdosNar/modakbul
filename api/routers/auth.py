from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from schemas.auth import UserCreate, UserDelete, TokenResponse
import services.auth_service as auth_service
from core.security import create_access_token
from api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED, summary="회원가입")
def signup(user_data: UserCreate):
    """새로운 사용자를 DB에 등록합니다.

    Args:
        user_data (UserCreate): 클라이언트가 전달한 회원가입 정보(username, password, nickname)

    Returns:
        dict: 회원가입 성공 메시지
    
    Raises:
        UserAlreadyExistsException: (CRUD 내부에서 발생) 이미 존재하는 아이디일 경우 409 반환
    """
    new_user = auth_service.create_user(user_data.username, user_data.password, user_data.nickname)
    return {
        "message" : "회원가입이 완료되었습니다.",
        "user": new_user
    }


@router.post("/login", response_model=TokenResponse, summary="로그인 및 토큰 발급")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """사용자 자격 증명을 확인하고 JWT 액세스 토큰을 발급합니다.

    FastAPI의 OAuth2PasswodRequestForm을 사용하여
    application/x-www-form-urlencoded 형식으로 데이터를 받습니다.

    Args:
        form_data (OAuth2PasswordRequestForm): 클라이언트가 전달한 username과 password

    Returns:
        TokenResponse: 발급된 JWT 액세스 토큰과 토큰 타입(bearer)
    """
    user = auth_service.authenticate_user(username=form_data.username, plain_password=form_data.password)
    token_data = {"sub": str(user["id"])}
    access_token = create_access_token(data=token_data)
    return {
        "access_token": access_token,
        "token_type" : "bearer"
    }


@router.post("/logout", summary="로그아웃 및 토큰 삭제 유도 응답")
def logout():
    """현재 로그인된 사용자의 로그아웃 처리를 수행합니다.

    JWT는 무상태(Stateless) 토큰이므로, 서버 측 세션 삭제 대신
    클라이언트에게 토큰 삭제를 유도하는 응답을 보냅니다.

    Returns:
        dict: 로그아웃 성공 메시지
    """
    return {"message" : "로그아웃 되었습니다."}


@router.delete("/me", response_model=dict, summary="현재 로그인한 사용자 삭제")
def withdraw(user_data: UserDelete, current_user_id: int = Depends(get_current_user)):
    """현재 로그인한 사용자의 계정을 영구 삭제합니다.

    본인 확인을 위해 비밀번호를 입력받으며, 확인이 완료되면 DB에서 유저를 삭제합니다.
    (연관된 모닥불 및 장작은 DB의 ON DELETE 제약조건에 따라 처리됨)

    Args:
        user_data (UserDelete): 클라이언트가 전달한 본인 확인용 비밀번호
        current_user_id (int): Depends를 통해 주입된 현재 로그인 사용자의 고유 ID

    Returns:
        dict: 회원 탈퇴 성공 메시지

    Raises:
        InvalidCredentialException: (CRUD 내부에서 발생) 비밀번호가 틀릴 경우 401 반환
    """
    auth_service.delete_user(user_data.password, current_user_id)
    return {"message" : "회원 탈퇴가 완료되었습니다."}
    

@router.get("/me", summary="현재 로그인한 사용자 정보 조회")
def read_users_me(current_user_id: int = Depends(get_current_user)):
    """현재 로그인한 사용자의 정보를 조회합니다.

    인증된 유저만 접근할 수 있는 엔드포인트입니다.

    Args:
        current_user_id (int): Depends를 통해 주입된 현재 로그인 사용자의 고유 ID

    Returns:
        dict: 현재 로그인한 사용자의 정보
    """
    return {
        "message": "인증 통과",
        "user_id": current_user_id
    }