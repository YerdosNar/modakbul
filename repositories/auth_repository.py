import sqlite3
from typing import Optional
from db.connection import get_db_connection
from core.exceptions import DBIntegrityError
from core.time_utils import get_now_iso

# CRUD - Create

def create_user(username: str, hashed_password: str, nickname: str) -> dict:
    """새로운 유저 데이터를 테이블에 삽입합니다.

    Args:
        username (str): 사용자의 username(ID).
        hashed_password (str): 암호화(해싱) 처리가 완료된 비밀번호 해시값.
        nickname (str): 서비스 내에서 표시할 사용자의 닉네임.

    Returns:
        dict: 생성된 유저 정보가 담긴 딕셔너리 (id, username, nickname 포함).

    Raises:
        sqlite3.IntegrityError: 아이디 중복 등의 유니크 제약조건을 위반할 경우 발생.
        sqlite3.Error: 데이터베이스 삽입 과정에서 데이터베이스 관련 오류가 발생할 경우 발생.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "INSERT INTO users (username, password_hash, nickname, created_at) VALUES (?, ?, ?, ?)"
        try:
            cursor.execute(query, (username, hashed_password, nickname, get_now_iso()))
            conn.commit()
            new_user_id = cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            raise DBIntegrityError(str(e))
        
        return {
            "id": new_user_id,
            "username": username,
            "nickname": nickname
        }

# CRUD - Read

def find_user_by_username_or_nickname(username: str, nickname: str) -> Optional[dict]:
    """username 또는 nickname으로 중복된 사용자가 있는지 조회합니다.
    
    DB connection의 절약을 위해 존재하는 함수로, 회원가입 시 username과 nickname 중복 체크를 한 번의 쿼리로 처리합니다.

    Args:
        username (str): 중복 여부를 확인할 사용자의 아이디 (username).
        nickname (str): 중복 여부를 확인할 사용자의 닉네임 (nickname).
    
    Returns:
        Optional[dict]: 중복된 사용자가 존재할 경우 해당 사용자 정보(username, nickname)가 담긴 딕셔너리,
                        존재하지 않을 경우 None을 반환.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 데이터베이스 관련 오류가 발생할 경우 발생.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT username, nickname FROM users WHERE username = ? OR nickname = ?"
        cursor.execute(query, (username, nickname))
        user = cursor.fetchone()
        return dict(user) if user else None


def get_user_by_username(username: str) -> Optional[dict]:
    """사용자의 username(ID)를 기준으로 사용자 정보를 레코드에서 탐색합니다.
    
    로그인 자격 인증용 사용자 정보를 조회할 때 사용합니다.

    Args:
        username (str): 인증 정보를 조회할 대상 사용자의 아이디.

    Returns:
        Optional[dict]: 조회 성공 시 사용자의 핵심 정보(id, username, nickname, password_hash)가 담긴 딕셔너리,
                        존재하지 않는 사용자일 경우 None을 반환합니다.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 데이터베이스 관련 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, username, nickname, password_hash FROM users WHERE username = ?"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return dict(user) if user else None


def get_hashed_password_by_user_id(user_id: int) -> Optional[str]:
    """사용자의 레코드 ID를 기준으로 사용자 정보를 레코드에서 탐색하여 해싱된 비밀번호를 반환합니다.
    
    탈퇴 검증을 위해 사용합니다.

    Args:
        user_id (int): 해시 비밀번호를 조회할 대상 사용자의 고유 식별 번호.

    Returns:
        Optional[str]: 해당 사용자의 해싱된 비밀번호 문자열, 유저가 존재하지 않을 경우 None을 반환합니다.

    Raises:
        sqlite3.Error: 데이터베이스 조회 과정에서 데이터베이스 관련 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT password_hash FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        return result["password_hash"] if result else None


# CRUD - Update : 없음

# CRUD - Delete

def delete_user_by_id(user_id: int) -> int:
    """사용자의 레코드 ID를 기준으로 사용자의 정보를 삭제합니다.
    
    삭제된 사용자 정보는 복구할 수 없으며, 삭제된 사용자와 관련된 모든 데이터도 함께 삭제됩니다.

    Args:
        user_id (int): 삭제할 사용자의 고유 식별 번호.

    Returns:
        int: 삭제 연산으로 인해 영향을 받은 행(row)의 개수 (정상 삭제 시 1 반환).

    Raises:
        sqlite3.Error: 데이터베이스 삭제 과정에서 데이터베이스 관련 오류가 발생할 경우 발생합니다.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "DELETE FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        return cursor.rowcount