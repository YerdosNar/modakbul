# 가변 연소율 및 수명 연장 시간 계산 모듈
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


def calculate_extension_timedelta(comment_count: int, oxygen_factor: float = 1.0) -> timedelta:
    """현재 장작(댓글) 개수와 산소 계수를 기반으로 연장할 시간(timedelta)을 계산합니다.
    
    가변 연소율 알고리즘에 적용하여 댓글이 누적될수록 추가 시간이 지수적으로 감쇠합니다.
    최소 연장 제한을 10초로 설정하여 극단적인 데이터 폭발을 안정적으로 방어하되,
    인위적인 일괄 시간제한 장벽을 해체하여 모닥불의 지연 연소 법칙을 보증합니다.

    Args:
        comment_count (int): 특정 모닥불(Topic)에 달린 장작(Comment)의 총 개수
        oxygen_factor (float, optional): 시맨틱 공간의 산소 밀도 계수 (0.3 ~ 1.0). 기본값 1.0.
    
    Returns:
        timedelta: 연장할 시간량 객체
    """

    # 기본 분 단위에 60을 곱해 초 단위로 환상
    base_seconds = settings.BASE_MINUTES * 60.0
    decay_power = settings.DECAY_RATE ** comment_count

    # 가변 연소율 및 산소 감쇠 계산
    calculated_seconds = base_seconds * decay_power * oxygen_factor

    # 최소 수명 연장 하한선 (10초) 설정하여 데이터 무한 폭증 방지
    final_seconds = max(10.0, calculated_seconds)

    return timedelta(seconds=final_seconds)


def get_new_expires_at(
        created_at: datetime,
        current_expires_at: datetime,
        comment_count: int,
        oxygen_factor: float = 1.0) -> datetime:
    """가변 연소율 및 산소 경쟁 시스템을 적용하여 연장된 새로운 만료 일시를 반환합니다.

    인위적인 Hard Limit(예: 24시간 절대 제한)을 제거하여, 활동성이 유지되는 한
    자연법칙에 의해 계속 타오를 수 있도록 보장합니다.

    Args:
        created_at (datetime): 모닥불이 처음 피워진 시간 (인식용)
        current_expires_at (datetime): 모닥불의 현재 만료 시간
        comment_count (int): 현재까지 달린 장작(Comment)의 총 개수
        oxygen_factor (float, optional): 시맨틱 공간의 산소 밀도 계수 (0.3 ~ 1.0). 기본값 1.0.
    
    Returns:
        datetime: 연장 계산이 완료된 최종 만료 시간 객체
    
    """
    extend_td = calculate_extension_timedelta(comment_count, oxygen_factor)
    return current_expires_at + extend_td