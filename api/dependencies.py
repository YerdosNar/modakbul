# 토큰 검증, 로그인 유저 식별 등 공통 함수 (Depends)

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from core.exceptions import InvalidCredentialsException
from core.security import SECRET_KEY, ALGORITHM

# Set Basic URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    """ 헤더의 JWT 토큰을 검증하고 현재 인증된 사용자의 고유 ID를 반환합니다.

    FastAPI의 Depends를 통해 Router에 주입되며,
    토큰의 유효성(만료 여부, 변조 여부)를 검사한 뒤 페이로드에서 유저 식별자(sub)를 추출합니다.

    Args:
        token (str): HTTP bearer 헤더에서 추출된 JWT 액세스 토큰

    Returns:
        int: 토큰에서 추출된 사용자의 고유 식별 번호 (user_id)
    
    Raises:
        invalidCredentialException: 다음과 같은 경우에 발생합니다.
            1. 토큰의 서명이 일치하지 않거나 조작된 경우 (DecodeError)
            2. 토큰의 유효 기간이 만료된 경우 (ExpiredSignatureError)
            3. 토큰 페이로드에 사용자 정보(sub)가 누락된 경우
    """
    
    
    """
    TODO: [?] JWT 토큰 해독 및 검증 로직 구현
    1. jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])를 사용하여 해독 시도
    2. 만약 jwt.PyJWTError 관련 예외가 발생하면 InvalidCredentialsException() 던지기
    3. 해독된 페이로드(payload.get("sub"))에서 user_id를 추출
    4. user_id가 없거나 타입이 올바르지 않아도 InvalidCredentialsException() 던지기
    """

    try:

        # 1. JWT 토큰 해독 및 검증 시도
        # JWT 자체 에러 발생 가능성 있음
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 3. payload에서 user_id 추출
        # JWT 특성 상 user_id는 문자열로 반환됨
        user_id_str = payload.get("sub")

        # 4. 누락 검증
        if user_id_str is None:
            raise InvalidCredentialsException()
        
        # 리턴 타입(int)에 맞게 형변환하여 반환
        return int(user_id_str)

    except jwt.PyJWTError:
        # 2. 서명 오류, 만료 등 JWT 자체에서 에러 발생할 수 있음
        raise InvalidCredentialsException()
    
    except ValueError:
        # sub에 숫자가 아닌 문자열이 들어가 int() 변환이 불가할 경우
        raise InvalidCredentialsException()