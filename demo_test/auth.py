import requests
import json

def signup(url: str, data: dict):
    """singup API 테스트"""
    return json.dumps(requests.post(url, json=data).json(), indent=2, ensure_ascii=False)

def login(url: str, data: dict):
    """login API 테스트"""
    return json.dumps(requests.post(url, data=data).json(), indent=2, ensure_ascii=False)

def login2(url: str, data: dict):
    """login API 테스트"""
    return requests.post(url, data=data).json()

def logout(url: str):
    """logout API 테스트"""
    return json.dumps(requests.post(url).json(), indent=2, ensure_ascii=False)

def get_me(url, token):
    """GET /me API 테스트"""
    return json.dumps(requests.get(url, headers={"Authorization": f"Bearer {token}"}).json(), indent=2, ensure_ascii=False)

def delete_me(url, header, payload):
    """DELETE /me API 테스트"""
    return json.dumps(requests.delete(url, headers=header, json=payload).json(), indent=2, ensure_ascii=False)