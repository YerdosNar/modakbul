import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
import sqlite3
from core.config import settings

def test_create_topic_unauthorized_fails(client: TestClient):
    """로그인하지 않은 사용자가 모닥불을 피우려고 시도할 때 401 에러를 반환하는지 검증합니다."""
    response = client.post(
        "/api/topics/",
        json={"content": "인증되지 않은 사용자가 피우는 모닥불"}
    )
    assert response.status_code == 401

def test_create_topic_success(client: TestClient):
    """인증된 사용자가 정상적으로 모닥불을 생성하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "첫 번째 모닥불을 피워봅니다."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "첫 번째 모닥불을 피워봅니다."
    assert data["comment_count"] == 0
    assert "expires_at" in data
    
    expires_at = datetime.fromisoformat(data["expires_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = expires_at - now
    assert 55 * 60 < diff.total_seconds() < 65 * 60

def test_create_topic_duplicate_content_fails(client: TestClient):
    """현재 활성화되어 있는 모닥불과 동일한 내용으로 생성 시도 시 409 Conflict를 반환하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "중복 글 방지 테스트 주제"}
    )
    
    response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "중복 글 방지 테스트 주제"}
    )
    assert response.status_code == 409
    assert "이미 같은 내용의 모닥불" in response.json()["detail"]

def test_similarity_auto_mapping_on_creation(client: TestClient):
    """유사한 주제의 모닥불이 피어날 때 코사인 유사도를 계산하여 매핑 기록이 DB에 벌크 인서트되는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 1. 원본 주제 모닥불 생성
    resp1 = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "맥북 프로 M4 대학생 할인 구매 갠춘함?"}
    )
    topic_id_1 = resp1.json()["id"]
    
    # 2. 유사도가 높은 모닥불 생성 (거의 동일한 내용으로 0.75 임계치 초과 보장)
    resp2 = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "맥북 프로 M4 대학생 할인 구매 갠춘함? 진짜로?"}
    )
    topic_id_2 = resp2.json()["id"]
    
    # DB 조회하여 topic_similarities 에 유사도 매핑이 생성되었는지 검증
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT similarity FROM topic_similarities WHERE (topic_id_1 = ? AND topic_id_2 = ?) OR (topic_id_1 = ? AND topic_id_2 = ?)",
        (topic_id_1, topic_id_2, topic_id_2, topic_id_1)
    )
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] >= 0.75


def test_create_topic_empty_fields_fail(client: TestClient):
    """빈 내용으로 모닥불 생성 시도 시 422 에러가 발생하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": ""}
    )
    assert response.status_code == 422




