# JWT 시크릿 키, 만료 시간 등 상수 관리

#setting
import os
from dotenv import load_dotenv
from core.exceptions import MissingEnvVarError, InvalidVarTypeError

class Settings:
    def __init__(self):
        load_dotenv()
        
        # 1. 기본 설정 및 DB 경로 추출
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise MissingEnvVarError("DATABASE_URL")
        
        # sqlite:///./modakbul.db 에서 파일명(modakbul.db)만 추출
        self.DB_FILENAME = self.DATABASE_URL.replace("sqlite:///", "").split("/")[-1]
        
        try:
            self.PORT = int(os.getenv("PORT", 8000))
            
            # 2. security 상수
            self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
            self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
            
            # 3. burn_rate 상수
            self.BASE_MINUTES = float(os.getenv("BASE_MINUTES", 10.0))
            self.DECAY_RATE = float(os.getenv("DECAY_RATE", 0.90))
            self.MAX_LIFESPAN_HOURS = int(os.getenv("MAX_LIFESPAN_HOURS", 24))
            
            # 4. DB Schema Limits 파싱
            self.USERNAME_LENGTH_MAX = int(os.getenv("USERNAME_LENGTH_MAX", 31))
            self.NICKNAME_LENGTH_MAX = int(os.getenv("NICKNAME_LENGTH_MAX", 31))
            self.TOPIC_LENGTH_MAX = int(os.getenv("TOPIC_LENGTH_MAX", 127))
            self.COMMENT_LENGTH_MAX = int(os.getenv("COMMENT_LENGTH_MAX", 1023))
            
        except (ValueError, TypeError):
            raise InvalidVarTypeError("환경 변수 타입 오류: 정수나 실수형 확인 필요")

def load_settings():
    return Settings()

settings = load_settings()