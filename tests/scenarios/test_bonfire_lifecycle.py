import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import sqlite3
from core.config import settings
from jobs.scheduler import garbage_collect

def test_bonfire_entire_lifecycle_scenario(client: TestClient):
    """[모닥불 생명주기 전체 시나리오]
    모닥불 생성 ──► 장작(댓글) 투척 및 수명 연장 ──► 만료 시각 도과 ──► Lazy Deletion 작동 ──►
    GC 백그라운드 아카이브 및 삭제 ──► 꺼진 모닥불(재) 피드 조회 성공 흐름을 통합 검증합니다.
    """
    # 1. 작성자 유저 생성 및 로그인
    client.post("/api/auth/signup", json={"username": "author", "password": "password", "nickname": "방장"})
    token_author = client.post("/api/auth/login", data={"username": "author", "password": "password"}).json()["access_token"]
    
    # 2. 모닥불 생성 (초기 수명 1시간)
    topic_resp = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token_author}"},
        json={"content": "라이프사이클 통합 테스트 모닥불"}
    )
    assert topic_resp.status_code == 201
    topic_id = topic_resp.json()["id"]
    initial_expires = datetime.fromisoformat(topic_resp.json()["expires_at"].replace("Z", "+00:00"))
    
    # 3. 댓글 작성자 유저 생성 및 로그인
    client.post("/api/auth/signup", json={"username": "commenter", "password": "password", "nickname": "구경꾼"})
    token_commenter = client.post("/api/auth/login", data={"username": "commenter", "password": "password"}).json()["access_token"]
    
    # 4. 장작(댓글) 투척 및 수명 연장 검증 (기본 10분 연장 검증)
    comment_resp = client.post(
        f"/api/topics/{topic_id}/comments",
        headers={"Authorization": f"Bearer {token_commenter}"},
        json={"content": "장작 추가요!"}
    )
    assert comment_resp.status_code == 201
    
    # 5. 연장 상태 확인
    topic_after = client.get(f"/api/topics/{topic_id}").json()
    assert topic_after["comment_count"] == 1
    after_expires = datetime.fromisoformat(topic_after["expires_at"].replace("Z", "+00:00"))
    assert (after_expires - initial_expires).total_seconds() == 600.0
    
    # 6. [시나리오 시뮬레이션] 만료 시각을 강제로 2시간 전으로 조작 (DB 직접 수정)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    cursor.execute("UPDATE topics SET expires_at = ? WHERE id = ?", (past_iso, topic_id))
    conn.commit()
    conn.close()
    
    # 7. 피드 조회 시 Lazy Deletion 작동하여 활성 목록에서 제외 확인
    feed_resp = client.get("/api/topics/")
    assert len(feed_resp.json()) == 0
    
    # 8. 백그라운드 가비지 컬렉터(GC) 수동 트리거 실행
    garbage_collect()
    
    # 9. 물리 테이블에서 데이터가 완전히 지워졌는지 확인 (정합성 검증)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM topics WHERE id = ?", (topic_id,))
    assert cursor.fetchone() is None
    cursor.execute("SELECT id FROM comments WHERE topic_id = ?", (topic_id,))
    assert cursor.fetchone() is None
    conn.close()
    
    # 10. 꺼진 피드(재) 조회 API를 통해 이관 데이터 정상 조회 확인
    ash_feed_resp = client.get("/api/topics/ashes")
    assert ash_feed_resp.status_code == 200
    ash_feed = ash_feed_resp.json()
    assert len(ash_feed) == 1
    assert ash_feed[0]["content"] == "라이프사이클 통합 테스트 모닥불"
    assert ash_feed[0]["comment_count"] == 1
