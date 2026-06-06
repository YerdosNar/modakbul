from datetime import datetime, timezone, timedelta

def get_now() -> datetime:
    """프로젝트 표준 시간대(UTC) 기준의 현재 datetime 객체를 반환합니다."""
    return datetime.now(timezone.utc)

def get_now_iso() -> str:
    """프로젝트 표준 포맷의 현재 시각 ISO 8601 문자열을 반환합니다."""
    return get_now().isoformat()

def parse_iso(iso_str: str) -> datetime:
    """ISO 8601 문자열을 UTC 시간대가 보정된 datetime 객체로 파싱합니다."""
    return datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)

def add_hours(dt: datetime, hours: int) -> datetime:
    """특정 시간 객체에 지정한 시간(Hour)만큼을 더해 반환합니다."""
    return dt + timedelta(hours=hours)
