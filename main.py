# FastAPI 앱 실행의 진입점

from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.init_db import init_db
from api.routers import auth, topics, comments
from jobs.scheduler import scheduler

# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize Database
    init_db()

    # Start Garbage Collector
    scheduler.start()

    yield

    # Shutdown Garbage Collector
    scheduler.shutdown()


app = FastAPI(
    title="Modakbul API",
    description="시간이 지나면 꺼지는 휘발성 모닥불 커뮤니티",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(auth.router, prefix="/api")
app.include_router(topics.router, prefix="/api")
app.include_router(comments.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message" : "모닥불(Modakbul) 서버가 활활 타오르고 있습니다."
    }

#setting
import sys
from core.config import settings
from db.connection import check_db_connection
from core.exceptions import ConfigException

try:
    check_db_connection(settings.DATABASE_URL)
    print("✅ 서버 가동 준비 완료")
except ConfigException as e:
    print(f"❌ 가동 실패: {e.detail}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 알 수 없는 오류 발생: {str(e)}")
    sys.exit(1)