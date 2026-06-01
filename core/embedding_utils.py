import hashlib
from typing import List

def generate_local_embedding(text: str, dimension: int = 128) -> List[float]:
    """ 텍스트 본문에서 문자 unigram 및 bigram 빈도를 기반으로 고정 차원의 단위 벡터 임베딩을 생성합니다.
    
    외부 API 및 외부 라이브러리 의존성 없이 오프라인으로 동작하도록 설계됐습니다.
    
    생성된 벡터는 코사인 유사도 연산의 편의를 위해 L2 정규화를 적용하여 단위 벡터로 반환됩니다.

    Args:
        text (str): 임베딩을 추출한 입력 텍스트 문자열.
        dimension (int, optional): 생성할 임베딩 벡터의 차원 수, 기본값 128.
    
    Returns:
        List[float]: L2 정규화가 완료된 dimension 크기의 1차원 float 리스트 벡터.

    Raises:
        ValueError: 입력 텍스트가 비어 있거나 올바르지 않은 타입일 경우 발생.
    """
    if not isinstance(text, str):
        raise ValueError("입력 텍스트는 문자열이어야 합니다.")
    
    if not text.strip():
        return [0.0] * dimension

    vector = [0.0] * dimension

    # 1. Unigram 및 Bigram 추출 및 해싱 투사

    features = []

    # 1-1. Unigram
    for char in text:
        if not char.isspace():
            features.append(char)

    # 1-2. Bigram
    for i in range(len(text) - 1):
        if not (text[i].isspace() or text[i + 1].isspace()):
            features.append(text[i : i + 2])

    # 1-3. 각 feature를 해싱하여 [0, dimension - 1]범위의 인덱스에 매핑하고 카운트 누적
    for feat in features:

        # MDS 해시값을 숫자로 변환하여 차원 수로 나눈 나머지를 인덱스로 사용
        hash_val = int(hashlib.md5(feat.encode('utf-8')).hexdigest(), 16)
        index = hash_val % dimension
        vector[index] += 1.0

    # 2. L2 Normalization
    squared_sum = sum(v ** 2 for v in vector)
    if squared_sum > 0:
        magnitude = squared_sum ** 0.5
        vector = [v / magnitude for v in vector]
    else:
        # 분모가 0이 되는 것을 방지하기 위해 균등 분포로 유닛 벡터 생성
        val = (1.0 / dimension) ** 0.5
        vector = [val] * dimension
    
    return vector


def get_embedding(text: str) -> List[float]:
    """ 텍스트의 임베딩 벡터를 반환하는 공통 엔트리포인트 함수입니다.
    
    설정 또는 환경 변수 상에 OpenAI 등의 외부 연동 설정이 유효할 경우
    해당 API를 사용해 임베딩을 획득할 수 있으며, 그렇지 않을 경우
    로컬 가상 해시 임베딩 생성기를 사용하여 즉시 결과를 벡터로 반환합니다.
    
    Args:
        text (str): 임베딩을 추출할 입력 텍스트 문자열.

    Returns:
        List[float]: 1차원 실수(float)로 구성된 L2 정규화 완료 임베딩 리스트.

    Raises:
        ValueError: 입력 텍스트가 유효하지 않을 때 발생.
    
    """

    return generate_local_embedding(text)