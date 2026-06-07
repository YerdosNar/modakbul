import pytest
from fastapi.testclient import TestClient

def test_user_entire_lifecycle_scenario(client: TestClient):
    """[사용자 전체 라이프사이클 시나리오]
    가입 ──► 로그인 ──► 토큰 획득 ──► 정보 조회 ──► 회원 탈퇴 ──► 탈퇴 검증으로 이어지는 흐름을 테스트합니다.
    """
    # 1. 회원 가입 성공
    signup_resp = client.post(
        "/api/auth/signup",
        json={"username": "scenario_user", "password": "password123", "nickname": "시나리오"}
    )
    assert signup_resp.status_code == 201
    
    # 2. 로그인 및 JWT 토큰 발급
    login_resp = client.post(
        "/api/auth/login",
        data={"username": "scenario_user", "password": "password123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    
    # 3. 토큰을 이용한 회원 정보 조회 (인증 인가 테스트)
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["user_id"] is not None
    
    # 4. 본인 패스워드 검증을 동반한 계정 탈퇴
    withdraw_resp = client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"password": "password123"}
    )
    assert withdraw_resp.status_code == 200
    
    # 5. 탈퇴 완료 후 로그인 재시도 시 접속 불가 검증
    login_retry = client.post(
        "/api/auth/login",
        data={"username": "scenario_user", "password": "password123"}
    )
    assert login_retry.status_code == 401
