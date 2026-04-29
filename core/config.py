# JWT 시크릿 키, 만료 시간 등 상수 관리

#setting
import os
from dotenv import load_dotenv
from core.exceptions import MissingEnvVarError, InvalidVarTypeError


class Settings:
    def __init__(self):
        load_dotenv()
        
        # 기본 설정
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise MissingEnvVarError("DATABASE_URL")
        
        try:
            self.PORT = int(os.getenv("PORT", 8000))
            
            # security 상수
            self.SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
            self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
            self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
            
            # burn_rate 상수
            self.BASE_MINUTES = float(os.getenv("BASE_MINUTES", 10.0))
            self.DECAY_RATE = float(os.getenv("DECAY_RATE", 0.90))
            self.MAX_LIFESPAN_HOURS = int(os.getenv("MAX_LIFESPAN_HOURS", 24))
            
        except (ValueError, TypeError):
            raise InvalidVarTypeError("환경 변수 타입 오류")

def load_settings():
    return Settings()

# 다른 파일에서 편하게 쓰도록 객체 생성
settings = load_settings()