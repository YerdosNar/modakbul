import pytest
from core.embedding_utils import get_embedding

def test_local_embedding_l2_normalization():
    """생성된 로컬 임베딩 벡터가 정상적으로 L2 정규화(단위 벡터) 되었는지 검증합니다."""
    text = "테스트용 노트북 맥북 구매 질문입니다."
    vector = get_embedding(text)
    
    # 1. 차원 크기 검증 (128차원)
    assert len(vector) == 128
    
    # 2. L2 Norm (크기) 계산 시 거의 1.0이 되는지 확인
    l2_norm = sum(v ** 2 for v in vector) ** 0.5
    
    # 윈도우 인코딩 cp949 우회용 출력
    print(f"\n      [DATA] 입력(텍스트)  | '{text}'")
    print(f"      [DATA] 결과(L2 Norm) | 예상: 1.0  |  실제: {l2_norm:.6f}  |  차원수: {len(vector)}차원")
    print(f"      [DATA] 벡터 샘플(앞 5차원): {vector[:5]}")
    
    assert pytest.approx(l2_norm, abs=1e-5) == 1.0

def test_local_embedding_empty_text():
    """빈 텍스트 입력 시 0.0 벡터를 반환하거나 예외를 방어하는지 검증합니다."""
    text = "   "
    vector = get_embedding(text)
    print(f"\n      [DATA] 입력(빈 텍스트) | '{text}' -> 결과 벡터 128차원이 모두 0.0 인지 검증")
    assert all(v == 0.0 for v in vector)

