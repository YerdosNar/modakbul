import requests
import json

def create_topic(url: str, headers, data: dict):
    """create_topic API 테스트"""
    return json.dumps(requests.post(url, headers=headers, json=data).json(), indent=2, ensure_ascii=False)

def get_topics(url: str, query_params: dict = None):
    """get_topics API 테스트"""
    return json.dumps(requests.get(url, params=query_params).json(), indent=2, ensure_ascii=False)
