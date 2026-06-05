import sqlite3
from core.exceptions import (
    UserAlreadyExistsException,
    UsernameAlreadyExistsException,
    NicknameAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException
)
from core.security import get_password_hash, verify_password
import repositories.auth_repository as auth_repo

def create_user(username: str, password: str, nickname: str) -> dict:
    """새로운 사용자 가입 처리를 검증 및 진행합니다."""
    try:
        existing_user = auth_repo.exists_user_by_username_or_nickname(username, nickname)

        if existing_user:
            if existing_user['username'] == username:
                raise UsernameAlreadyExistsException()
            if existing_user['nickname'] == nickname:
                raise NicknameAlreadyExistsException()
            
        hashed_password = get_password_hash(password)
        return auth_repo.create_user(username=username, hashed_password=hashed_password, nickname=nickname)
        
    except sqlite3.IntegrityError:
        raise UserAlreadyExistsException()

def authenticate_user(username: str, plain_password: str) -> dict:
    """아이디 및 해시 비밀번호 정합성을 일괄 분석 검증합니다."""
    user = auth_repo.get_user_by_username(username)

    if not user:
        raise InvalidCredentialsException()

    if not verify_password(plain_password, user["password_hash"]):
        raise InvalidCredentialsException()

    return {
        "id": user["id"],
        "username": user["username"],
        "nickname": user["nickname"]
    }

def delete_user(plain_password: str, user_id: int) -> dict:
    """비밀번호 대조 후 유저 정보를 안전하게 하드 삭제 유도합니다."""
    hashed_password = auth_repo.get_hashed_password_by_user_id(user_id)

    if hashed_password is None:
        raise UserNotFoundException()
    
    if not verify_password(plain_password, hashed_password):
        raise InvalidCredentialsException()
    
    affected_rows = auth_repo.delete_user_by_id(user_id)
    return {
        "deleted_user_id": user_id,
        "affected_rows": affected_rows
    }