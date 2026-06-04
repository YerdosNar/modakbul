from typing import List

def calculate_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """두 1차원 실수 벡터 간의 코사인 유사도(Cosine Similarity)를 계산합니다.

    외부 라이브러리 없이 파이썬만으로 계산하며,
    분모가 0이 되는 것을 방지하도록 설계되었습니다.

    Args:
        vec1 (List[float]): 첫 번째 비교 대상 벡터
        vec2 (List[float]): 두 번째 비교 대상 벡터

    Returns:
        float: -1.0에서 1.0 사이의 코사인 유사도 값, 한 벡터가 제로 벡터일 경우 0.0 반환

    Raises:
        ValueError: 두 벡터의 차원 수(크기)가 일치하지 않을 때 발생
    """

    if len(vec1) != len(vec2):
        raise ValueError(f"두 벡터의 크기가 일치하지 않습니다. (vec1: {len(vec1)}, vec2: {len(vec2)})")

    # 분자: Dot Product
    dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))

    # 분모: L2 Norm (크기) 곱
    norm1 = sum(v ** 2 for v in vec1) ** 0.5
    norm2 = sum(v ** 2 for v in vec2) ** 0.5

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    # 부동 소수점 오차에 따른 코사인 유사도 범위를 [-1.0 ~ 1.0]으로 조정
    similarity = dot_product / (norm1 * norm2)
    return max(-1.0, min(1.0, similarity))