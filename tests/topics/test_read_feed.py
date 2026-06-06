import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import sqlite3
from core.config import settings

def test_read_active_topics_feed_lazy_deletion(client: TestClient):
    """피드 조회 시, 수명이 남아있는 모닥불만 보이고 만료 시각이 지난 모닥불은 노출되지 않는지(Lazy Deletion) 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 1. 살아있는 방 생성
    client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "신선하게 불타오르는 모닥불"}
    )
    
    # 2. 이미 만료된 글 강제 삽입 (직접 DB를 조작하여 만료 상태인 데이터 인위적 생성)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    cursor.execute(
        "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("이미 꺼져버린 차가운 모닥불", past_iso, 0, 0, past_iso, 1)
    )
    conn.commit()
    conn.close()
    
    # 3. 피드 조회 API 요청
    response = client.get("/api/topics/")
    assert response.status_code == 200
    feed = response.json()
    
    # 만료된 모닥불은 Lazy Deletion 필터로 인해 보이지 않고 살아있는 것만 보여야 함
    assert len(feed) == 1
    assert feed[0]["content"] == "신선하게 불타오르는 모닥불"
