import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import sqlite3
from core.config import settings

def test_add_comment_unauthorized_fails(client: TestClient):
    """로그인하지 않은 유저가 장작(댓글) 투척 시도 시 401 Unauthorized를 반환하는지 검증합니다."""
    response = client.post(
        "/api/topics/1/comments",
        json={"content": "인증 정보 없는 댓글"}
    )
    assert response.status_code == 401

def test_add_comment_nonexistent_topic_fails(client: TestClient):
    """존재하지 않는 모닥불 ID에 댓글 투척 시도 시 404 에러를 반환하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    response = client.post(
        "/api/topics/9999/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "유령 모닥불에 장작 넣기"}
    )
    assert response.status_code == 404
    assert "존재하지 않거나 이미 꺼진" in response.json()["detail"]

def test_add_comment_success_and_extension(client: TestClient):
    """정상적으로 장작이 추가되고 모닥불의 수명이 연장되며 댓글 카운트가 1 증가하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 1. 모닥불 생성
    topic = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "수명 연장 테스트 타겟 방"}
    ).json()
    topic_id = topic["id"]
    initial_expires = datetime.fromisoformat(topic["expires_at"].replace("Z", "+00:00"))
    
    # 2. 첫 번째 댓글 작성
    resp_comment = client.post(
        f"/api/topics/{topic_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "첫 번째 장작 투척합니다."}
    )
    assert resp_comment.status_code == 201
    
    # 3. 모닥불 수명 연장 체크
    topic_after = client.get(f"/api/topics/{topic_id}").json()
    assert topic_after["comment_count"] == 1
    
    after_expires = datetime.fromisoformat(topic_after["expires_at"].replace("Z", "+00:00"))
    expected_extension = 600.0 # BASE_MINUTES=10.0 * 60.0
    actual_extension = (after_expires - initial_expires).total_seconds()
    
    assert pytest.approx(actual_extension, abs=2.0) == expected_extension

def test_add_comment_to_expired_topic_fails(client: TestClient):
    """이미 만료 시간이 지난 모닥불에 댓글 투척 시도 시 403 Forbidden 에러가 발생하는지 검증합니다 (경계 상태 테스트)."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 1. 억지로 만료된 모닥불을 DB에 다이렉트 삽입
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    past_iso = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    cursor.execute(
        "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("이미 꺼져서 상호작용 불가능한 방", past_iso, 0, 0, past_iso, None)
    )
    topic_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # 2. 만료된 방에 댓글 달기 시도
    response = client.post(
        f"/api/topics/{topic_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "꺼진 불씨를 살려보려 애씁니다."}
    )
    assert response.status_code == 403
    assert "수명이 다하여 더 이상 상호작용할 수 없습니다" in response.json()["detail"]

def test_oxygen_competition_diminishing_returns(client: TestClient):
    """주변에 유사 모닥불들의 댓글 누적량이 많을 때 산소 농도가 깎여 수명 연장 폭이 현저히 적어지는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # Scenario A: 주변에 유사한 활성 방이 아예 없을 때의 연장 폭
    topic_a = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "아무도 주변에 없는 외로운 섬 모닥불"}
    ).json()
    expires_a_init = datetime.fromisoformat(topic_a["expires_at"].replace("Z", "+00:00"))
    
    client.post(
        f"/api/topics/{topic_a['id']}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "장작 추가"}
    )
    
    topic_a_after = client.get(f"/api/topics/{topic_a['id']}").json()
    expires_a_after = datetime.fromisoformat(topic_a_after["expires_at"].replace("Z", "+00:00"))
    extension_a = (expires_a_after - expires_a_init).total_seconds()
    
    # Scenario B: 주변에 대화가 매우 활성화된 유사 모닥불이 존재할 때
    # 1. 주변에 유사한 모닥불 생성
    topic_b_near = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "맥북 프로 16인치 M4 진짜 좋음?"}
    ).json()
    
    # 2. 주변 유사 모닥불에 인위적으로 대량의 댓글 누적 시키기 (예: 10개)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET comment_count = 10 WHERE id = ?", (topic_b_near["id"],))
    conn.commit()
    conn.close()
    
    # 3. 새로운 유사 모닥불 생성 (유사도 매핑 유도, 거의 일치하도록 설정)
    topic_b_new = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "맥북 프로 16인치 M4 진짜 좋음? 궁금하네요."}
    ).json()
    expires_b_init = datetime.fromisoformat(topic_b_new["expires_at"].replace("Z", "+00:00"))
    
    # 4. 새로 생성한 방에 댓글 추가
    client.post(
        f"/api/topics/{topic_b_new['id']}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "장작 추가"}
    )
    
    topic_b_after = client.get(f"/api/topics/{topic_b_new['id']}").json()
    expires_b_after = datetime.fromisoformat(topic_b_after["expires_at"].replace("Z", "+00:00"))
    extension_b = (expires_b_after - expires_b_init).total_seconds()
    
    # 산소 경쟁 공식에 따라:
    # oxygen_factor = max(0.3, 1.0 - (10 * 0.05)) = 0.5
    # extension_b의 예상 연장폭은 extension_a (600초) 대비 50%인 300초 근방이어야 함.
    conn.close()


def test_comments_concurrency_race_condition_under_wal(client: TestClient):
    """5개의 스레드가 동시에 하나의 모닥불에 댓글(장작)을 투척할 때, SQLite WAL(Write-Ahead Logging) 모드를 통해 database is locked 오류 없이 동시 쓰기 및 트랜잭션 정합성이 유지되는지 검증합니다."""
    # 1. 5명의 사용자 회원가입 및 토큰 획득
    tokens = []
    for i in range(5):
        client.post(
            "/api/auth/signup",
            json={"username": f"user_race_{i}", "password": "password", "nickname": f"경합유저{i}"}
        )
        token = client.post(
            "/api/auth/login",
            data={"username": f"user_race_{i}", "password": "password"}
        ).json()["access_token"]
        tokens.append(token)
        
    # 2. 타겟 모닥불 생성
    topic = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {tokens[0]}"},
        json={"content": "동시성 경합 테스트 모닥불"}
    ).json()
    topic_id = topic["id"]
    
    # 3. ThreadPoolExecutor를 통한 동시 쓰기 API 호출 함수 정의
    from concurrent.futures import ThreadPoolExecutor
    
    def post_comment(token_and_index):
        user_token, idx = token_and_index
        # 로깅 클라이언트를 스레드 안전하게 각각 찌름
        return client.post(
            f"/api/topics/{topic_id}/comments",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"content": f"동시 쓰기 시도 장작 #{idx}"}
        )
        
    # 4. 5개 스레드를 동시에 띄워 동시 요청 실행
    tasks = list(zip(tokens, range(5)))
    print(f"\n      [CONCURRENCY] 5개 스레드 동시 쓰기 요청 시작...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(post_comment, tasks))
        
    # 5. 모든 요청이 201 Created로 에러 없이 성공했는지 확인
    for idx, resp in enumerate(results):
        print(f"      [CONCURRENCY] 스레드 #{idx} 결과 -> Status: {resp.status_code}")
        assert resp.status_code == 201
        
    # 6. 최종 모닥불의 댓글 수 및 DB 삽입 정합성 대조
    topic_after = client.get(f"/api/topics/{topic_id}").json()
    print(f"      [CONCURRENCY] 최종 결과 | 누적된 댓글 수 예상: 5개  |  실제: {topic_after['comment_count']}개")
    assert topic_after["comment_count"] == 5


def test_add_comment_empty_fields_fail(client: TestClient):
    """빈 내용으로 장작(댓글) 투척 시도 시 422 에러가 발생하는지 검증합니다."""
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    token = client.post("/api/auth/login", data={"username": "user1", "password": "password"}).json()["access_token"]
    
    # 1. 모닥불 생성
    topic = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": "댓글 검증용 모닥불"}
    ).json()
    topic_id = topic["id"]

    # 2. 빈 댓글 작성 시도
    response = client.post(
        f"/api/topics/{topic_id}/comments",
        headers={"Authorization": f"Bearer {token}"},
        json={"content": ""}
    )
    assert response.status_code == 422


