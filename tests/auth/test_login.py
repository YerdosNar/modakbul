import pytest
from fastapi.testclient import TestClient

def test_login_success_and_jwt_token(client: TestClient):
    """로그인 성공 시 JWT 액세스 토큰이 발급되는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "loginuser", "password": "correctpassword", "nickname": "로그인테스트"}
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "loginuser", "password": "correctpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials_fails(client: TestClient):
    """존재하지 않는 아이디 또는 틀린 비밀번호 시도 시 동일한 401 오류 메시지를 던지는지 검증합니다 (보안성 검증)."""
    client.post(
        "/api/auth/signup",
        json={"username": "existuser", "password": "password123", "nickname": "실제유저"}
    )
    
    # 1. 존재하지 않는 아이디로 로그인 시도
    response_nonexist = client.post(
        "/api/auth/login",
        data={"username": "nonexistuser", "password": "password123"}
    )
    
    # 2. 존재하는 아이디에 틀린 비밀번호로 로그인 시도
    response_wrongpw = client.post(
        "/api/auth/login",
        data={"username": "existuser", "password": "wrongpassword"}
    )
    
    # 두 경우 모두 보안상 에러 코드와 디테일 메시지가 일치해야 함
    assert response_nonexist.status_code == 401
    assert response_wrongpw.status_code == 401
    
    msg_nonexist = response_nonexist.json()["detail"]
    msg_wrongpw = response_wrongpw.json()["detail"]
    assert msg_nonexist == msg_wrongpw
    assert msg_nonexist == "로그인 정보가 일치하지 않습니다."
