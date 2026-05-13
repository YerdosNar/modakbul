import json
import sys
from datetime import datetime
from util import print_result
from auth import signup, login, login2, logout, get_me, delete_me
from topic import create_topic, get_topics
from comment import create_comment, get_comments, get_comments_2

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

if __name__ == "__main__":

    # 로그인

    user_data = {
        "username" : "topic",
        "password" : "1234",
        "nickname" : "feat_topic"
    }

    signup_result = signup(f"{BASE_URL}/api/auth/signup", user_data)

    login_data = {
        "username" : user_data["username"],
        "password" : user_data["password"]
    }
    login_result = login2(f"{BASE_URL}/api/auth/login", login_data)
    token = login_result["access_token"]
    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "password": user_data["password"]
    }
    
    print()
    print("모닥불(Topic)과 장작(Comment)을 위한 로그인")
    print(f"user_data : \t{user_data}")
    print(f"token : \t{token}")
    print(f"headers : \t{headers}")
    print(f"payload : \t{payload}")
    print()
    
    # 모닥불 피우기 (Topic 생성)
    topic_data = {
        "content" : "Topic_1"
    }
    create_topic_result = create_topic(f"{BASE_URL}/api/topics", headers, topic_data)
    print_result("create_topic", "정상", topic_data, create_topic_result)

    # 모닥불 피우기 (Topic 생성)
    topic_data = {
        "content" : "Topic_2"
    }
    create_topic_result = create_topic(f"{BASE_URL}/api/topics", headers, topic_data)
    print_result("create_topic", "정상", topic_data, create_topic_result)

    page_condition = {
        "limit" : 1,
        "offset" : 0
    }

    print("\n2번 모닥불(Topic)에 장작(Comment) 7개 추가하며 만료 기한 연장 데이터 수집 중...\n")
    times = []
    for i in range(2, 9):
        comment_data = {
            "content" : f"Comment_{i}"
        }
        create_comment(f"{BASE_URL}/api/topics/2/comments", headers, comment_data)
        times.append(get_comments_2(f"{BASE_URL}/api/topics/2", page_condition)["expires_at"])
    print("\n장작 추가 완료!\n")

    # 연장 시간 증감률 

    print("모닥불 시간 연장 시간 증감률")
    dt_times = [datetime.fromisoformat(t.replace("Z", "+00:00")) for t in times]

    for t in dt_times:
        print(t)

    print(len(dt_times))
    for i in range(1, len(dt_times)):
        time_diff = dt_times[i] - dt_times[i - 1]
        added_seconds = time_diff.total_seconds()
        minutes, seconds = divmod(added_seconds, 60)
        print(f"▶ 장작 {i}개 누적 시: 수명이 +{int(minutes)}분 {int(seconds)}초 ({int(added_seconds)}초) 연장됨")

