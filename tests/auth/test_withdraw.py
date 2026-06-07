import pytest
from fastapi.testclient import TestClient

def test_user_withdrawal_success(client: TestClient):
    """탈퇴 시 올바른 비밀번호를 입력하면 계정 삭제가 성공하는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "quituser", "password": "quitpassword", "nickname": "탈퇴자"}
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "quituser", "password": "quitpassword"}
    )
    token = login_resp.json()["access_token"]
    
    # 올바른 패스워드로 탈퇴 요청
    response = client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "quitpassword"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "회원 탈퇴가 완료되었습니다."
    
    # 탈퇴 후 다시 로그인 시도 시 실패해야 함
    login_retry = client.post(
        "/api/auth/login",
        data={"username": "quituser", "password": "quitpassword"}
    )
    assert login_retry.status_code == 401

def test_user_withdrawal_wrong_password_fails(client: TestClient):
    """탈퇴 시 비밀번호가 일치하지 않으면 401 에러를 반환하고 계정이 보존되는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "keepuser", "password": "keeppassword", "nickname": "보존유저"}
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "keepuser", "password": "keeppassword"}
    )
    token = login_resp.json()["access_token"]
    
    # 잘못된 비밀번호로 탈퇴 시도
    response = client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "wrongpassword"}
    )
    assert response.status_code == 401
    
    # 여전히 로그인이 잘 되는지 확인 (탈퇴 처리되지 않았음)
    login_retry = client.post(
        "/api/auth/login",
        data={"username": "keepuser", "password": "keeppassword"}
    )
    assert login_retry.status_code == 200

def test_user_withdrawal_empty_password_fail(client: TestClient):
    """빈 비밀번호로 회원 탈퇴 시도 시 422 에러가 발생하는지 검증합니다."""
    client.post(
        "/api/auth/signup",
        json={"username": "quituser", "password": "quitpassword", "nickname": "탈퇴자"}
    )
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "quituser", "password": "quitpassword"}
    )
    token = login_resp.json()["access_token"]
    
    response = client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": ""}
    )
    assert response.status_code == 422
