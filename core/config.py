# JWT 시크릿 키, 만료 시간 등 상수 관리

#setting
import os
from dotenv import load_dotenv
from core.exceptions import MissingEnvVarError, InvalidVarTypeError

class Settings:
    def __init__(self):
        load_dotenv()
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            raise MissingEnvVarError("DATABASE_URL")
            
        try:
            self.PORT = int(os.getenv("PORT", 8000))
        except (ValueError, TypeError):
            raise InvalidVarTypeError("PORT")

def load_settings():
    return Settings()