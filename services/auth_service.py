from core.exceptions import (
    UserAlreadyExistsException,
    UsernameAlreadyExistsException,
    NicknameAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
    DBIntegrityError
)
from core.security import get_password_hash, verify_password
import repositories.auth_repository as auth_repo

def create_user(username: str, password: str, nickname: str) -> dict:
    """새로운 사용자 가입 처리를 검증 및 진행합니다.

    입력받은 평문 비밀번호는 내부적으로 단방향 해싱(bcrypt) 처리되어 저장됩니다.

    Args:
        username (str): 가입할 사용자의 ID
        password (str): 가입할 사용자의 평문 비밀번호
        nickname (str): 가입할 사용자의 닉네임
         
    Returns:
        dict: 생성된 사용자의 정보 (password_hash는 제외)

    Raises:
        UserAlreadyExistsException: 입력한 username(ID)이 이미 DB에 존재할 경우 발생
    """

    existing_user = auth_repo.find_user_by_username_or_nickname(username, nickname)

    if existing_user:
        if existing_user['username'] == username:
            raise UsernameAlreadyExistsException()
        
        if existing_user['nickname'] == nickname:
            raise NicknameAlreadyExistsException()
        
    hashed_password = get_password_hash(password)
    try:
        return auth_repo.create_user(username=username, hashed_password=hashed_password, nickname=nickname)
    except DBIntegrityError:
        raise UserAlreadyExistsException()

def authenticate_user(username: str, plain_password: str) -> dict:
    """ 사용자의 로그인 자격 증명을 검증합니다.

    DB에 해당 ID가 존재하는지 먼저 확인하고,
    입력된 평문 비밀번호와 DB의 해시된 비밀번호가 일치하는지 검증합니다.

    Args:
        username (str): 로그인 시도하는 사용자의 ID
        password (str): 로그인 시도하는 사용자의 평문 비밀번호
    
    Returns:
        dict: 인증에 성공한 사용자의 DB 레코드 정보

    Raises:
        InvalidCredentialsException: 아이디가 존재하지 않거나, 비밀번호가 틀릴 경우 발생

    """
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
    """유저 ID와 비밀번호를 검증한 후, DB에서 유저를 영구 삭제합니다.

    Args:
        password (str): 본인 확인을 위한 평문 비밀번호
        user_id (int): 삭제할 유저의 고유 ID

    Raises:
        InvalidCredentialsException: 비밀번호가 일치하지 않을 때 발생
        UserNotFoundException: 해당 유저가 DB에 없을 때 발생
    
    """
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