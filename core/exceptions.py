from fastapi import HTTPException

class ModakbulException(HTTPException):
    """ 프로젝트 최상위 예외 클래스 """

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

# =============================
# Auth / User Domain Exception
# =============================

class UserAlreadyExistsException(ModakbulException):
    """ 이미 존재하는 user 정보로 회원가입을 시도할 때 발생하는 예외 """
    def __init__(self, detail: str = "이미 존재하는 ID입니다."):
        super().__init__(status_code=409, detail=detail)

class UsernameAlreadyExistsException(ModakbulException):
    """ 이미 존재하는 username으로 회원가입을 시도할 때 발생하는 예외 """
    def __init__(self, detail: str = "이미 존재하는 ID입니다."):
        super().__init__(status_code=409, detail=detail)

class NicknameAlreadyExistsException(ModakbulException):
    """ 이미 존재하는 nickname으로 회원가입을 시도할 때 발생하는 예외 """
    def __init__(self, detail: str = "이미 존재하는 Nickname입니다."):
        super().__init__(status_code=409, detail=detail)

class UserNotFoundException(ModakbulException):
    """ 유저를 찾을 수 없을 때 발생하는 예외 """
    def __init__(self, detail: str = "존재하지 않는 유저입니다."):
        super().__init__(status_code=404, detail=detail)

class InvalidCredentialsException(ModakbulException):
    """ 로그인 정보가 일치하지 않을 때 발생하는 예외 """
    def __init__(self, detail: str = "로그인 정보가 일치하지 않습니다."):
        super().__init__(status_code=401, detail=detail)


# ==============================
# 모닥불(Topic) Domain Exception
# ==============================

class TopicNotFoundException(ModakbulException):
    """ 모닥불을 찾을 수 없거나 이미 꺼졌을 때 발생하는 예외 """
    def __init__(self, detail: str = "존재하지 않거나 이미 꺼진 모닥불입니다."):
        super().__init__(status_code=404, detail=detail)

class TopicAlreadyExistsException(ModakbulException):
    def __init__(self, detail: str = "이미 같은 내용의 모닥불이 피어있습니다."):
        super().__init__(status_code=409, detail=detail)

class TopicAlreadyExpiredException(ModakbulException):
    def __init__(self):
        super().__init__(status_code=403, detail="이 모닥불은 수명이 다하여 더 이상 상호작용할 수 없습니다.")

class InvalidTopicContentException(ModakbulException):
    def __init__(self):
        super().__init__(status_code=422, detail="모닥불의 내용이 비어있거나 너무 깁니다.")

# ==============================
# 장작(Comment) Domain Exception
# ==============================

class InvalidCommentContentException(ModakbulException):
    def __init__(self):
        super().__init__(status_code=422, detail="장작의 내용이 비어있거나 너무 깁니다.")


# setting
class ConfigException(ModakbulException):
    def __init__(self, detail: str = "System Configuration Error"):
        super().__init__(status_code=500, detail=detail)

class MissingEnvVarError(ConfigException):
    def __init__(self, var_name: str):
        super().__init__(detail=f"필수 환경 변수 누락: {var_name}")

class InvalidVarTypeError(ConfigException):
    def __init__(self, var_name: str):
        super().__init__(detail=f"변수 타입 데이터 불일치: {var_name}")

class ResourceAccessError(ConfigException):
    def __init__(self, message: str = "DB 연결 실패"):
        super().__init__(detail=message)