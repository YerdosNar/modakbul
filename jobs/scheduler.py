# scheduler.py - APScheduler, 만료 모닥불 물리 삭제 로직

import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from db.connection import get_db_connection
from datetime import datetime, timedelta, timezone
from core.config import settings

interval = settings.GARBAGE_COLLECTION_INTERVAL

def garbage_collect():
    
    """ 유효 기간이 지난 Topic과 Comment를 DB에서 삭제합니다.
    
    만료되었거나 아직 활성 상태인 모닥불을 '재(is_ash = 1)'로 전환하며,
    한 번 '재'가 된 데이터는 영구 보존하여 아카이빙합니다.
    """

    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON")

            # 만료된 활성 모닥불을 '재(is_ash = 1'로 상태 업데이트
            query = "UPDATE topics SET is_ash = 1 WHERE expires_at < ? AND is_ash = 0"
            cursor.execute(query, (now_iso,))

            # 재로 변환된 topic 개수 확인
            ash_count = cursor.rowcount
            
            # DB에 반영
            conn.commit()

            if ash_count > 0:
                print(f"[GC] Success : {ash_count}개의 모닥불이 재(Ash) 상태로 아카이빙됐습니다.")
            else:
                print("[GC] : 정리할 모닥불 대상이 없습니다.")
    
    except Exception as e:
        print(f"[GC] Error: {e}")

def gc_job_runner():
    """주기적으로 garbage collect를 진행합니다.
    """
    garbage_collect()

scheduler = BackgroundScheduler()

scheduler.add_job(gc_job_runner, 'interval', seconds=interval)
        

            
