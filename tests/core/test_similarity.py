import pytest
from core.similarity import calculate_cosine_similarity

def test_cosine_similarity_calculation():
    """동일 벡터 및 상이한 벡터 간 코사인 유사도 연산의 타당성을 검증합니다."""
    vec1 = [1.0, 0.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0, 0.0]
    
    # 1. 동일 벡터 유사도 연산
    sim_same = calculate_cosine_similarity(vec1, vec2)
    print(f"\n      [DATA] 입력(동일 벡터) | vec1: {vec1}, vec2: {vec2} -> 유사도: {sim_same}")
    assert pytest.approx(sim_same, abs=1e-5) == 1.0
    
    # 2. 직교 벡터 유사도 연산
    vec3 = [0.0, 1.0, 0.0, 0.0]
    sim_ortho = calculate_cosine_similarity(vec1, vec3)
    print(f"      [DATA] 입력(직교 벡터) | vec1: {vec1}, vec2: {vec3} -> 유사도: {sim_ortho}")
    assert pytest.approx(sim_ortho, abs=1e-5) == 0.0

def test_cosine_similarity_dimension_mismatch():
    """차원이 맞지 않는 벡터 연산 시 ValueError 발생 여부를 검증합니다."""
    vec_a = [1.0, 2.0]
    vec_b = [1.0, 2.0, 3.0]
    print(f"\n      [DATA] 입력(차원 미스매치) | vec1: {vec_a} (2차원), vec2: {vec_b} (3차원) -> ValueError 발생 예상")
    with pytest.raises(ValueError):
        calculate_cosine_similarity(vec_a, vec_b)

