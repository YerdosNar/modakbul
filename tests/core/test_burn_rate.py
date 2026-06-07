import pytest
from core.burn_rate import calculate_extension_timedelta

def test_burn_rate_decay_by_comments():
    """댓글 개수가 많아질수록 지수적으로 수명 연장 단위가 감쇠하는지 검증합니다."""
    # 댓글 0개일 때의 연장 시간
    time_0 = calculate_extension_timedelta(comment_count=0)
    print(f"\n      [DATA] 입력(댓글 0개)  |  예상: 600.0초  |  실제: {time_0.total_seconds()}초")
    
    # 댓글 5개일 때의 연장 시간 (600 * 0.90^5 = 354.29)
    time_5 = calculate_extension_timedelta(comment_count=5)
    print(f"      [DATA] 입력(댓글 5개)  |  예상: ~354.3초  |  실제: {time_5.total_seconds():.2f}초")
    
    # 댓글 20개일 때의 연장 시간 (600 * 0.90^20 = 73.0)
    time_20 = calculate_extension_timedelta(comment_count=20)
    print(f"      [DATA] 입력(댓글 20개) |  예상: ~73.0초   |  실제: {time_20.total_seconds():.2f}초")
    
    assert time_0.total_seconds() > time_5.total_seconds()
    assert time_5.total_seconds() > time_20.total_seconds()

def test_burn_rate_minimum_limit():
    """댓글이 극단적으로 많아져도 연장 하한선(10초) 아래로 내려가지 않는지 검증합니다 (경계값 테스트)."""
    # 댓글 500개 상황 시뮬레이션
    extended_time = calculate_extension_timedelta(comment_count=500)
    print(f"\n      [DATA] 입력(댓글 500개) |  예상: 10.0초   |  실제: {extended_time.total_seconds()}초")
    
    assert extended_time.total_seconds() == 10.0

def test_burn_rate_oxygen_factor_impact():
    """산소 농도가 낮아질수록(주변 대화 과열) 수명 연장 폭이 추가로 감쇠하는지 검증합니다."""
    # 산소 충만 상태 (oxygen_factor = 1.0)
    time_oxygen_rich = calculate_extension_timedelta(comment_count=5, oxygen_factor=1.0)
    print(f"\n      [DATA] 입력(산소 100%) |  예상: ~354.3초  |  실제: {time_oxygen_rich.total_seconds():.2f}초")
    
    # 산소 희박 상태 (oxygen_factor = 0.3)
    time_oxygen_poor = calculate_extension_timedelta(comment_count=5, oxygen_factor=0.3)
    print(f"      [DATA] 입력(산소  30%) |  예상: ~106.3초  |  실제: {time_oxygen_poor.total_seconds():.2f}초")
    
    assert time_oxygen_rich.total_seconds() > time_oxygen_poor.total_seconds()
    ratio = time_oxygen_poor.total_seconds() / time_oxygen_rich.total_seconds()
    assert pytest.approx(ratio, abs=0.05) == 0.3

