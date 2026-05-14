# bcrypt 해싱 함수, JWT 생성 함수 등
import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from core.config import settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_password_hash(password: str) -> str:
    """평문 비밀번호를 단방향 암호화(해싱)하여 반환합니다.

    보안을 위해 bcrypt 알고리즘을 적용하여 솔트(Salt)가 포함된 해시값을 생성합니다.
    
    Args:
        password (str): 사용자가 입력한 평문 비밀번호

    Returns:
        str: DB에 안전하게 저장할 수 있는 해싱된 비밀번호 문자열

    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """로그인 시 입력받은 평문 비밀번호가 DB의 해시와 일치하는지 검증합니다.

    Args:
        plain_password (str): 사용자가 로그인 폼에 입력한 평문 비밀번호
        hashed_password (str): DB에 저장되어 있던 해시된 비밀번호

    Returns:
        bool: 두 비밀번호가 일치하면 True, 틀리면 False
    
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """사용자 식별 데이터를 담은 JWT(JSON Web Token) 액세스 토큰을 생성합니다.

    보안을 위해 전달받은 페이로드(data)에 토큰 만료 시간(exp)을 자동으로 추가한 뒤 서명하여 반환합니다.

    Args:
        data (dict): 토큰 페이로드에 담을 데이터 (예: {"sub": "user_id"})

    Returns:
        str: 헤더(Header), 페이로드(Payload), 서명(Signature)이 포함된 JWT 문자열
    
    """

    # 1. 원본 데이터의 훼손 방지를 위해 딕셔너리 복사
    to_encode = data.copy()

    # 2. 'exp' (만료 시간) 키 추가
    # 서버 위치에 상관없이 동일하게 동작하도록 UTC 시간을 기준으로 함
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # 3. SECRET_KEY와 HS256 알고리즘을 사용해 토큰 생성 후 반환
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
