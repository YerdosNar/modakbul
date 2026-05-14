# 가변 연소율 계산
# 가변 연소율 계산

import math
from datetime import datetime, timedelta
from core.config import settings

# 모닥불 상수 선언
# BASE_MINUTES = 10.0
# DECAY_RATE = 0.90
# MAX_LIFESPAN_HOURS = 24

def calculate_extension_minutes(comment_count: int) -> int:
    """현재 장작(댓글) 개수를 기반으로 연장할 시간(분)을 계산합니다.

    Args:
        comment_count (int): 특정 모닥불(Topic)에 달린 장작(Comment) 개수
    
    Returns:
        int: 연장할 시간(분)
    
    """
    return max(1, math.ceil(settings.BASE_MINUTES * (settings.DECAY_RATE ** comment_count)))

def get_new_expires_at(
        created_at: datetime,
        current_expires_at: datetime,
        comment_count: int) -> datetime:
    """가변 연소율 및 최대 수명 제한을 적용하여 새로운 만료 일시를 반환하빈다.

    Args:
        created_at (datetime): 모닥불이 처음 피워진 시간
        current_expires_at (datetime): 모닥불의 현재 만료 시간
        comment_count (int): 현재까지 달린 장작(Comment)의 총 개수
    
    Returns:
        datetime: Hard Limit가 적용된 최종 만료 시간
    
    """
    extend_minutes = calculate_extension_minutes(comment_count)
    new_expires_at = current_expires_at + timedelta(minutes=extend_minutes)

    # 최대 수명 제한
    max_possible_time = created_at + timedelta(hours=settings.MAX_LIFESPAN_HOURS)

    # 계산된 시간과 최대 수명 중 더 짧은 시간을 반환
    return min(new_expires_at, max_possible_time)