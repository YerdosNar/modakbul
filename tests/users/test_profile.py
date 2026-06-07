import pytest
import sqlite3
from fastapi.testclient import TestClient
from core.config import settings
from jobs.scheduler import garbage_collect

def test_get_user_profile_not_found(client: TestClient):
    """존재하지 않는 유저 ID로 프로필 조회 시 404 에러를 반환하는지 검증합니다."""
    response = client.get("/api/users/9999/profile")
    assert response.status_code == 404
    assert "존재하지 않는 유저입니다." in response.json()["detail"]


def test_get_user_profile_success(client: TestClient):
    """정상 가입된 사용자의 프로필 조회 시, 사용자가 작성한 모닥불과 장작 목록이 예쁘게 취합되는지 검증합니다."""
    # 1. 회원가입 및 로그인
    client.post("/api/auth/signup", json={"username": "profileuser", "password": "password", "nickname": "프로필맨"})
    login_resp = client.post("/api/auth/login", data={"username": "profileuser", "password": "password"}).json()
    token = login_resp["access_token"]
    
    # 내 유저 ID 확인하기 위해 내 정보 조회 호출
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_resp.json()["user_id"]

    # 2. 모닥불 작성
    topic_content = "프로필 테스트용 모닥불 주제"
    topic_resp = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": topic_content}
    )
    topic_id = topic_resp.json()["id"]

    # 3. 장작(댓글) 작성
    comment_content = "프로필 테스트용 장작 댓글"
    client.post(
        f"/api/topics/{topic_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": comment_content}
    )

    # 4. 통합 프로필 조회 API 호출
    response = client.get(f"/api/users/{user_id}/profile")
    assert response.status_code == 200
    
    data = response.json()
    
    # 4-1. 유저 정보 검증
    assert data["user"]["id"] == user_id
    assert data["user"]["username"] == "profileuser"
    assert data["user"]["nickname"] == "프로필맨"
    
    # 4-2. 최근 모닥불 검증
    assert len(data["recent_topics"]) == 1
    assert data["recent_topics"][0]["id"] == topic_id
    assert data["recent_topics"][0]["content"] == topic_content
    assert data["recent_topics"][0]["is_ash"] == 0

    # 4-3. 최근 댓글 검증
    assert len(data["recent_comments"]) == 1
    assert data["recent_comments"][0]["content"] == comment_content
    assert data["recent_comments"][0]["topic"]["id"] == topic_id
    assert data["recent_comments"][0]["topic"]["content"] == topic_content
    assert data["recent_comments"][0]["topic"]["is_ash"] == 0


def test_get_user_profile_with_expired_and_archived_activity(client: TestClient):
    """이미 만료되거나 가비지 컬렉터를 통해 아카이브 테이블로 이관된 모닥불과 댓글은 프로필에서 제외되는지 검증합니다."""
    # 1. 회원가입 및 로그인
    client.post("/api/auth/signup", json={"username": "archiveduser", "password": "password", "nickname": "아카이브맨"})
    login_resp = client.post("/api/auth/login", data={"username": "archiveduser", "password": "password"}).json()
    token = login_resp["access_token"]
    
    # 유저 ID 가져오기
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    user_id = me_resp.json()["user_id"]

    # 2. 첫 번째 모닥불 작성 (나중에 아카이브 이관될 대상)
    resp1 = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "곧 꺼져서 재가 될 첫 번째 모닥불"}
    )
    topic_id_1 = resp1.json()["id"]

    # 첫 번째 모닥불에 장작(댓글) 추가
    client.post(
        f"/api/topics/{topic_id_1}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "아카이브용 장작 댓글"}
    )

    # 3. 두 번째 모닥불 작성 (현재 활성 상태 유지)
    resp2 = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "여전히 활활 타오르는 두 번째 모닥불"}
    )
    topic_id_2 = resp2.json()["id"]

    client.post(
        f"/api/topics/{topic_id_2}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "활성 상태 장작 댓글"}
    )

    # 이관 전 검증: 두 모닥불과 두 댓글이 모두 조회되어야 함
    response_before = client.get(f"/api/users/{user_id}/profile")
    data_before = response_before.json()
    assert len(data_before["recent_topics"]) == 2
    assert len(data_before["recent_comments"]) == 2

    # 4. DB를 직접 수정하여 첫 번째 모닥불의 만료 시간(expires_at)을 과거로 변경
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET expires_at = '2020-01-01T00:00:00' WHERE id = ?", (topic_id_1,))
    conn.commit()
    conn.close()

    # 5. 가비지 컬렉터 수동 실행 -> 첫 번째 모닥불과 댓글이 ash_topics, ash_comments 로 강제 물리 이관됨
    garbage_collect()

    # 6. 통합 프로필 조회 API 호출
    response_after = client.get(f"/api/users/{user_id}/profile")
    assert response_after.status_code == 200
    
    data_after = response_after.json()
    
    # 6-1. 최근 모닥불 검증: 아카이브된 1번째 모닥불은 결과에서 제외되고 2번째 활성 모닥불만 반환되어야 함
    assert len(data_after["recent_topics"]) == 1
    assert data_after["recent_topics"][0]["id"] == topic_id_2
    assert data_after["recent_topics"][0]["is_ash"] == 0

    # 6-2. 최근 댓글 검증: 아카이브된 1번째 댓글은 결과에서 제외되고 2번째 활성 댓글만 반환되어야 함
    assert len(data_after["recent_comments"]) == 1
    assert data_after["recent_comments"][0]["content"] == "활성 상태 장작 댓글"
    assert data_after["recent_comments"][0]["topic"]["id"] == topic_id_2
    assert data_after["recent_comments"][0]["topic"]["is_ash"] == 0
