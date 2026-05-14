import requests
import json

def create_comment(url: str, headers, data: dict):
    """create_topic API 테스트"""
    return json.dumps(requests.post(url, headers=headers, json=data).json(), indent=2, ensure_ascii=False)

def get_comments(url: str, query_params: dict = None):
    """get_topics API 테스트"""
    return json.dumps(requests.get(url, params=query_params).json(), indent=2, ensure_ascii=False)

def get_comments_2(url: str, query_params: dict = None):
    """get_topics API 테스트"""
    return requests.get(url, params=query_params).json()
