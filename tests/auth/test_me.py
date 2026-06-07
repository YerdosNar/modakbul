import pytest
from fastapi.testclient import TestClient

def test_authenticate_current_user_me(client: TestClient):
    """발급된 JWT 토큰을 이용해 회원 정보 조회가 성공하는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "meuser", "password": "mypassword", "nickname": "나"}
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "meuser", "password": "mypassword"}
    )
    token = login_resp.json()["access_token"]
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "인증 통과"

def test_authenticate_invalid_token_fails(client: TestClient):
    """조작된 토큰 또는 잘못된 형식으로 인증 시도 시 401 Unauthorized 에러가 발생하는지 검증합니다."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-jwt-token-content"}
    )
    assert response.status_code == 401
