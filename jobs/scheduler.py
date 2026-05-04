# scheduler.py - APScheduler, 만료 모닥불 물리 삭제 로직

import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from db.connection import get_db_connection
from datetime import datetime, timedelta, timezone
from core.config import settings

interval = settings.GARBAGE_COLLECTION_INTERVAL

def garbage_collect():
    
    """ 유효 기간이 지난 Topic과 Comment를 DB에서 삭제합니다.
    
    해당 삭제는  백그라운드(Backgorund)에서 진행합니다.
    """

    now_str = datetime.now(timezone.utc)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA foreign_keys = ON")

            # 기간이 지난 topic 삭제
            query = "DELETE FROM topics WHERE expires_at < ?"
            cursor.execute(query, (now_str,))

            # 삭제된 topic 개수 확인
            deleted_count = cursor.rowcount
            
            # DB에 반영
            conn.commit()

            if deleted_count > 0:
                print(f"GC Success : {deleted_count} 삭제 완료.")
            else:
                print("GC : 삭제할 모닥불이 없습니다.")
    
    except Exception as e:
        print(f"GC Error: {e}")

def gc_job_runner():
    """주기적으로 garbage collect를 진행합니다.
    """
    garbage_collect()

scheduler = BackgroundScheduler()

scheduler.add_job(gc_job_runner, 'interval', seconds=interval)
        

            
