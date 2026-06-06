import pytest
from fastapi.testclient import TestClient

def test_signup_success(client: TestClient):
    """정상적인 정보로 회원가입이 성공하는지 검증합니다."""
    response = client.post(
        "/api/auth/signup",
        json={
            "username": "user123",
            "password": "securepassword",
            "nickname": "철수"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "회원가입이 완료되었습니다."
    assert data["user"]["username"] == "user123"
    assert data["user"]["nickname"] == "철수"
    assert "password" not in data["user"] # 비밀번호 해시 조차 응답 스펙 제외

def test_signup_duplicate_username_fails(client: TestClient):
    """중복된 아이디(username)로 가입 시도 시 409 에러가 발생하는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "duplicate", "password": "password", "nickname": "닉네임1"}
    )
    response = client.post(
        "/api/auth/signup",
        json={"username": "duplicate", "password": "different", "nickname": "닉네임2"}
    )
    assert response.status_code == 409
    assert "이미 존재하는 ID" in response.json()["detail"]

def test_signup_duplicate_nickname_fails(client: TestClient):
    """중복된 닉네임으로 가입 시도 시 409 에러가 발생하는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "user1", "password": "password", "nickname": "중복닉네임"}
    )
    response = client.post(
        "/api/auth/signup",
        json={"username": "user2", "password": "different", "nickname": "중복닉네임"}
    )
    assert response.status_code == 409
    assert "이미 존재하는 Nickname" in response.json()["detail"]

def test_signup_empty_fields_fail(client: TestClient):
    """빈 필드로 가입 시도 시 422 에러가 발생하는지 검증합니다."""
    response = client.post(
        "/api/auth/signup",
        json={"username": "", "password": "", "nickname": ""}
    )
    assert response.status_code == 422

