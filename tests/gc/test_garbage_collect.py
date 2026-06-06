import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta
import sqlite3
from core.config import settings
from jobs.scheduler import garbage_collect

def test_garbage_collector_logical_and_physical_archive(client: TestClient):
    """가비지 컬렉터가 작동하여 만료된 모닥불과 댓글을 1단계 논리 잠금(is_ash=1)한 뒤 2단계 아카이브 물리 이관하는지 검증합니다."""
    # 1. 테스트용 유저 가입
    client.post("/api/auth/signup", json={"username": "user1", "password": "password", "nickname": "닉네임1"})
    
    # 2. 임의로 모닥불 2개 직접 삽입 (직접 DB를 조작하여 만료 상태와 활성 상태 모닥불 시뮬레이션)
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    now = datetime.now(timezone.utc)
    past_iso = (now - timedelta(hours=1)).isoformat()
    future_iso = (now + timedelta(hours=1)).isoformat()
    
    # 만료된 모닥불 A 삽입 (user_id를 None으로 하여 외래키 제약조건 위반 방지)
    cursor.execute(
        "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("만료되어 정리되어야 할 모닥불 A", past_iso, 0, 0, past_iso, None)
    )
    topic_id_expired = cursor.lastrowid
    
    # 살아있는 모닥불 B 삽입
    cursor.execute(
        "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        ("살아남아야 할 활성 모닥불 B", future_iso, 0, 0, now.isoformat(), None)
    )
    topic_id_active = cursor.lastrowid
    
    # 만료된 모닥불 A 하위에 댓글(장작) 추가
    cursor.execute(
        "INSERT INTO comments (content, created_at, user_id, topic_id) VALUES (?, ?, ?, ?)",
        ("만료된 방의 장작", past_iso, None, topic_id_expired)
    )
    comment_id_expired = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    # 3. 가비지 컬렉션(GC) 수동 실행
    garbage_collect()
    
    # 4. DB 상태 확인 검증
    conn = sqlite3.connect(settings.DB_FILENAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 4-1. 활성 topics 테이블 검증
    # 만료된 A는 topics 테이블에서 물리적으로 삭제되어 있어야 함
    cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id_expired,))
    assert cursor.fetchone() is None
    
    # 살아있는 B는 topics 테이블에 안전하게 남아있어야 함
    cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id_active,))
    active_row = cursor.fetchone()
    assert active_row is not None
    assert active_row["content"] == "살아남아야 할 활성 모닥불 B"
    
    # 4-2. 활성 comments 테이블 검증
    # 만료된 A의 하위 댓글도 물리 삭제되어야 함
    cursor.execute("SELECT * FROM comments WHERE id = ?", (comment_id_expired,))
    assert cursor.fetchone() is None
    
    # 4-3. 아카이브 테이블(ash_topics, ash_comments) 이관 검증
    # 만료된 A가 아카이브 테이블로 정상 복사되었는지 검증
    cursor.execute("SELECT * FROM ash_topics WHERE id = ?", (topic_id_expired,))
    ash_topic_row = cursor.fetchone()
    assert ash_topic_row is not None
    assert ash_topic_row["content"] == "만료되어 정리되어야 할 모닥불 A"
    assert ash_topic_row["is_ash"] == 1
    
    # 만료된 A의 하위 댓글도 아카이브 테이블로 정상 이관되었는지 검증
    cursor.execute("SELECT * FROM ash_comments WHERE topic_id = ?", (topic_id_expired,))
    ash_comment_row = cursor.fetchone()
    assert ash_comment_row is not None
    assert ash_comment_row["content"] == "만료된 방의 장작"
    
    conn.close()


def test_garbage_collector_batch_boundary_cases(client: TestClient):
    """가비지 컬렉터 작동 시 만료된 데이터의 양이 BATCH_SIZE(10개)를 초과하는 경계 조건(12개 만료)에서도 루프를 돌며 누수 없이 전량 안전하게 이관/삭제하는지 검증합니다."""
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    # 1. BATCH_SIZE인 10개를 초과하는 12개의 만료 예정 모닥불을 DB에 강제 삽입
    now = datetime.now(timezone.utc)
    past_iso = (now - timedelta(hours=1)).isoformat()
    
    inserted_ids = []
    for i in range(12):
        cursor.execute(
            "INSERT INTO topics (content, expires_at, comment_count, is_ash, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (f"경계값 테스트용 만료 모닥불 {i}", past_iso, 0, 0, past_iso, None)
        )
        inserted_ids.append(cursor.lastrowid)
        
    conn.commit()
    conn.close()
    
    # 2. BATCH_SIZE가 10으로 고정된 상태에서 가비지 컬렉션 트리거
    # (내부적으로 BATCH_SIZE=10 크기씩 두 번의 청크 루프를 돌아야 완료됨)
    garbage_collect()
    
    # 3. 데이터 이관 결과 대조
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    # 3-1. 활성 topics 테이블에서는 12개 모두 삭제 완료 상태여야 함
    cursor.execute("SELECT COUNT(*) FROM topics WHERE id IN ({})".format(",".join("?" * 12)), inserted_ids)
    active_count = cursor.fetchone()[0]
    assert active_count == 0
    
    # 3-2. 아카이브 ash_topics 테이블에는 12개 모두 안전하게 들어와 있어야 함
    cursor.execute("SELECT COUNT(*) FROM ash_topics WHERE id IN ({})".format(",".join("?" * 12)), inserted_ids)
    archived_count = cursor.fetchone()[0]
    assert archived_count == 12
    
    conn.close()

