import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import sqlite3
from core.config import settings

def test_get_topic_detail_nonexistent_fails(client: TestClient):
    """존재하지 않는 모닥불 ID로 상세 조회를 시도하면 404 에러를 반환하는지 검증합니다."""
    response = client.get("/api/topics/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "존재하지 않거나 이미 꺼진 모닥불입니다."

def test_get_topic_detail_expired_active_returns_ash(client: TestClient):
    """물리적으로는 삭제되지 않았으나 만료 시간이 지나 꺼진(active 테이블에 존재) 모닥불의 상세 조회 시 200 응답과 함께 is_ash가 1로 가공되어 반환되는지 검증합니다."""
    # 1. 만료된 모닥불을 active 테이블에 직접 삽입
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc)
    past_iso = (now - timedelta(minutes=10)).isoformat()
    created_iso = (now - timedelta(hours=1)).isoformat()
    
    cursor.execute(
        "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("만료되었으나 아직 아카이브되지 않은 모닥불", past_iso, 0, 0, created_iso, None)
    )
    topic_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 2. 상세 조회 수행
    response = client.get(f"/api/topics/{topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == topic_id
    assert data["content"] == "만료되었으나 아직 아카이브되지 않은 모닥불"
    assert data["is_ash"] == 1

def test_get_topic_detail_archived_returns_ash(client: TestClient):
    """이미 가비지 컬렉터에 의해 아카이브 테이블(ash_topics/ash_comments)로 이관된 모닥불 상세 조회 시 200 응답 및 댓글 정상 조회를 검증합니다."""
    # 1. 아카이브 모닥불 및 댓글 직접 삽입
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc)
    past_iso = (now - timedelta(hours=2)).isoformat()
    
    cursor.execute(
        "INSERT INTO ash_topics (id, content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (999, "아카이브된 모닥불", past_iso, 2, 1, past_iso, None)
    )
    cursor.execute(
        "INSERT INTO ash_comments (id, content, created_at, user_id, topic_id) VALUES (?, ?, ?, ?, ?)",
        (8881, "아카이브된 첫 번째 댓글", past_iso, None, 999)
    )
    cursor.execute(
        "INSERT INTO ash_comments (id, content, created_at, user_id, topic_id) VALUES (?, ?, ?, ?, ?)",
        (8882, "아카이브된 두 번째 댓글", past_iso, None, 999)
    )
    conn.commit()
    conn.close()
    
    # 2. 상세 조회 수행
    response = client.get("/api/topics/999")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 999
    assert data["content"] == "아카이브된 모닥불"
    assert data["is_ash"] == 1
    assert len(data["comments"]) == 2
    # 최신순 정렬(created_at desc 또는 id desc)에 맞추어 검증
    # 인서트할 때 동일 past_iso 이므로 id가 큰 순서 혹은 입력 순서
    # comment_repo가 ORDER BY created_at DESC로 조회하므로, DB 엔진에 따라 id desc나 insert 역순으로 나옴
    comments = data["comments"]
    assert any(c["content"] == "아카이브된 첫 번째 댓글" for c in comments)
    assert any(c["content"] == "아카이브된 두 번째 댓글" for c in comments)

def test_get_topic_detail_comments_pagination(client: TestClient):
    """모닥불 상세 조회 시 댓글(장작) 목록이 limit와 offset에 따라 정상적으로 페이징(Pagination) 처리되는지 검증합니다."""
    # 1. 모닥불 생성
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    resp = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "댓글 페이징 테스트 방"}
    )
    topic_id = resp.json()["id"]
    
    # 2. 해당 모닥불에 25개의 댓글(장작) 삽입 (created_at을 1초씩 다르게 해서 역순 정렬 보장)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)
    for i in range(1, 26):
        comment_time = (now + timedelta(seconds=i)).isoformat()
        cursor.execute(
            "INSERT INTO comments (content, created_at, user_id, topic_id) VALUES (?, ?, ?, ?)",
            (f"테스트 댓글 {i:02d}", comment_time, None, topic_id)
        )
    # comment_count 업데이트
    cursor.execute("UPDATE topics SET comment_count = 25 WHERE id = ?", (topic_id,))
    conn.commit()
    conn.close()
    
    # 3. 1페이지 상세 조회 (limit=10, offset=0)
    resp_page1 = client.get(f"/api/topics/{topic_id}?limit=10&offset=0")
    assert resp_page1.status_code == 200
    comments_page1 = resp_page1.json()["comments"]
    assert len(comments_page1) == 10
    # ORDER BY created_at DESC 이므로 25번 댓글이 제일 처음 나옴
    assert comments_page1[0]["content"] == "테스트 댓글 25"
    assert comments_page1[9]["content"] == "테스트 댓글 16"
    
    # 4. 2페이지 상세 조회 (limit=10, offset=10)
    resp_page2 = client.get(f"/api/topics/{topic_id}?limit=10&offset=10")
    assert resp_page2.status_code == 200
    comments_page2 = resp_page2.json()["comments"]
    assert len(comments_page2) == 10
    assert comments_page2[0]["content"] == "테스트 댓글 15"
    assert comments_page2[9]["content"] == "테스트 댓글 06"
    
    # 5. 3페이지 상세 조회 (limit=10, offset=20)
    resp_page3 = client.get(f"/api/topics/{topic_id}?limit=10&offset=20")
    assert resp_page3.status_code == 200
    comments_page3 = resp_page3.json()["comments"]
    assert len(comments_page3) == 5
    assert comments_page3[0]["content"] == "테스트 댓글 05"
    assert comments_page3[4]["content"] == "테스트 댓글 01"
