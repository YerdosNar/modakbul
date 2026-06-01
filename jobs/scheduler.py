# scheduler.py - APScheduler, 만료 모닥불 물리 삭제 로직

import sqlite3
import time
from apscheduler.schedulers.background import BackgroundScheduler
from db.connection import get_db_connection
from datetime import datetime, timedelta, timezone
from core.config import settings

interval = settings.GARBAGE_COLLECTION_INTERVAL

def garbage_collect():
    """ 유효 기간이 지난 Topic과 Comment를 DB에서 영구 아카이브 테이블로 이관합니다.
    
    1단계: 만료된 모닥불을 즉시 논리 잠금(is_ash = 1)하여 추가 쓰기/댓글 조회를 전면 차단합니다.
    2단계: 잘게 쪼갠 청크 단위(ARCHIVE_BATCH_SIZE)로 아카이브 테이블로 안전하게 물리 이관한 뒤 삭제합니다.
    청크 이관 사이사이에 ARCHIVE_THROTTLE_INTERVAL 휴식을 주어 다른 사용자의 쓰기 락 획득 권한을 보장합니다.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    BATCH_SIZE = settings.ARCHIVE_BATCH_SIZE
    THROTTLE_INTERVAL = settings.ARCHIVE_THROTTLE_INTERVAL
    total_migrated = 0

    try:
        # [1단계: 논리 잠금] 만료된 모닥불을 빠르게 is_ash = 1 상태로 잠금
        # 이 연산은 대규모 락 유발 없이 1ms 내외로 즉시 완료됩니다
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("UPDATE topics SET is_ash = 1 WHERE expires_at < ? AND is_ash = 0", (now_iso,))
            conn.commit()

        # [2단계: 물리 청크 이관] is_ash = 1인 모닥불을 잘라서 천천히 아카이브 테이블로 복사 및 삭제
        while True:
            # 2-1. 이번 배치 청크에 이관할 대상 식별
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("SELECT id FROM topics WHERE is_ash = 1 LIMIT ?", (BATCH_SIZE,))
                expired_ids = [row["id"] for row in cursor.fetchall()]

            if not expired_ids:
                break

            # 2-2. 단일 청크 이관 트랜잭션 실행
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                
                for t_id in expired_ids:
                    # ash_topics 테이블로 복사
                    cursor.execute("""
                        INSERT OR IGNORE INTO ash_topics (id, content, comment_count, is_ash, created_at, expires_at, user_id)
                        SELECT id, content, comment_count, 1, created_at, expires_at, user_id
                        FROM topics WHERE id = ?
                    """, (t_id,))
                    
                    # ash_comments 테이블로 복사
                    cursor.execute("""
                        INSERT OR IGNORE INTO ash_comments (id, content, created_at, user_id, topic_id)
                        SELECT id, content, created_at, user_id, topic_id
                        FROM comments WHERE topic_id = ?
                    """, (t_id,))
                    
                    # 활성 topics 테이블에서 물리 삭제 (Cascade로 인해 active comments 및 similarities 자동 삭제)
                    cursor.execute("DELETE FROM topics WHERE id = ?", (t_id,))
                
                conn.commit()
                total_migrated += len(expired_ids)

            # 2-3. 잠시 휴식하여 데이터베이스가 다른 사용자의 요청(락)을 처리할 시간을 확보함 (Throttling)
            time.sleep(THROTTLE_INTERVAL)

        if total_migrated > 0:
            print(f"[GC] Success : {total_migrated}개의 만료된 모닥불과 하위 장작들을 논리 잠금 후 청크 단위로 안전하게 물리 이관 완료하였습니다.")
        else:
            print("[GC] : 정리할 만료된 모닥불 대상이 없습니다.")
            
    except Exception as e:
        print(f"[GC] Error: {e}")

def gc_job_runner():
    """주기적으로 garbage collect를 진행합니다.
    """
    garbage_collect()

scheduler = BackgroundScheduler()

scheduler.add_job(gc_job_runner, 'interval', seconds=interval)
        

            
