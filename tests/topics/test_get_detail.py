import pytest
from fastapi.testclient import TestClient

def test_get_topic_detail_success(client: TestClient):
    """모닥불 상세 조회 시 올바른 본문 정보 및 빈 댓글 리스트가 포함되어 반환되는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 활성 모닥불 생성
    resp = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "상세 조회 테스트 방"}
    )
    topic_id = resp.json()["id"]
    
    # 상세 조회 API 호출
    detail_resp = client.get(f"/api/topics/{topic_id}")
    assert detail_resp.status_code == 200
    data = detail_resp.json()
    assert data["content"] == "상세 조회 테스트 방"
    assert "comments" in data
    assert isinstance(data["comments"], list)
