import json
import sys
from datetime import datetime
from util import print_result
from auth import signup, login, login2, logout, delete_me
from topic import create_topic, get_topics
from comment import create_comment, get_comments, get_comments_2

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

if __name__ == "__main__":
    
    # [auth] ===================================================================

    # 회원가입
    user_data = {
        "username" : "auth",
        "password" : "1234",
        "nickname" : "feat_auth"
    }
    signup_result = signup(f"{BASE_URL}/api/auth/signup", user_data)
    print_result("signup", "정상", user_data, signup_result)

    # 회원가입 - ID 겹침
    user_data = {
        "username" : "auth",
        "password" : "1234",
        "nickname" : "feat_auth_2"
    }
    signup_result = signup(f"{BASE_URL}/api/auth/signup", user_data)
    print_result("signup", "ID 중복", user_data, signup_result)


    # 회원가입 - Nickname 겹침
    user_data = {
        "username" : "auth_2",
        "password" : "1234",
        "nickname" : "feat_auth"
    }
    signup_result = signup(f"{BASE_URL}/api/auth/signup", user_data)
    print_result("signup", "낙네임 중복", user_data, signup_result)

    #---------------------------------------------------------------------

    # 로그인
    user_data = {
        "username" : "auth",
        "password" : "1234",
    }
    login_result = login(f"{BASE_URL}/api/auth/login", user_data)
    print_result("Login", "정상", user_data, login_result)

    print()

    # 로그인 - 회원가입을 하지 않은 ID
    user_data = {
        "username" : "unknown",
        "password" : "1234"
    }
    login_result = login(f"{BASE_URL}/api/auth/login", user_data)
    print_result("Login", "가입한 ID가 아님", user_data, login_result)


    # 로그인 - 비밀번호 틀림
    user_data = {
        "username" : "auth",
        "password" : "12345"
    }
    login_result = login(f"{BASE_URL}/api/auth/login", user_data)
    print_result("Login", "비밀번호 틀림", user_data, login_result)

    print("가입을 하지 않은 ID나 비밀번호가 틀린 경우 모두 '로그인 정보 불일치'로 나타냄")
    print("이를 통해 무차별 ID 대입을 통한 가입 회원 유추 방어 가능")
    print()

    #---------------------------------------------------------------------

    # 로그아웃 - Token은 서버에서 관리하지 않고 소유자 스스로 파기하는 형태
    logout_result = logout(f"{BASE_URL}/api/auth/logout")
    print_result("Logout", "정상", "없음", logout_result)

    #---------------------------------------------------------------------

    # 계정 삭제 - 삭제됐다는 메시지만 남김
    user_data = {
        "username" : "auth",
        "password" : "1234",
    }
    login_result = login2(f"{BASE_URL}/api/auth/login", user_data)
    token = login_result["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "password": user_data["password"]
    }
    
    delete_me_result = delete_me(f"{BASE_URL}/api/auth/me", headers, payload)
    print_result("DELETE-me", "정상", {"headers" : headers, "payload" : payload}, delete_me_result)


    # ===================================================================

    print("=" * 50)

    # [topic] ===========================================================


    # 회원가입 및 로그인

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
    print("모닥불(Topic)과 장작(Comment)을 위한 새로운 회원가입 및 로그인")
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

    # 똑같은 내용으로 모닥불 피우기
    create_topic_result = create_topic(f"{BASE_URL}/api/topics", headers, topic_data)
    print_result("create_topic", "중복 등록", topic_data, create_topic_result)
    
    # 모닥불 약 14개 추가
    print("\n모닥불(topic) 9개 추가 중...\n")
    for i in range(2, 11):
        topic_data = {
            "content" : f"Topic_{i}"
        }
        create_topic(f"{BASE_URL}/api/topics", headers, topic_data)
    print("\n모닥불 추가 완료!\n")

    # 모닥불 가져오기 (페이징 지원)
    page_condition = {
        "limit" : 5,
        "offset" : 0
    }
    get_topics_result = get_topics(f"{BASE_URL}/api/topics", page_condition)
    print_result("get_topics", "10 ~ 6번 topic 조회", page_condition, get_topics_result)

    page_condition = {
        "limit" : 2,
        "offset" : 3
    }
    get_topics_result = get_topics(f"{BASE_URL}/api/topics", page_condition)
    print_result("get_topics", "7(10-offset) ~ 6번 topic 조회", page_condition, get_topics_result)


    # ===================================================================

    print("=" * 50)

    # [Comment] ===========================================================

    # 1번 topic 잔여 시간 조회
    page_condition = {
        "limit" : 1,
        "offset" : 0
    }
    get_comments_result = get_comments_2(f"{BASE_URL}/api/topics/1", page_condition)
    before_expires_at = get_comments_result["expires_at"]
    # 1번 topic에 comment 추가
    comment_data = {
        "content" : "Comment_1"
    }
    print("1번 topic에 commment 추가")
    create_comment_result = create_comment(f"{BASE_URL}/api/topics/1/comments", headers, comment_data)
    print_result("create_comment", "정상", comment_data, create_comment_result)
    
    # 1번 topic 잔여 시간 조회
    get_comments_result = get_comments_2(f"{BASE_URL}/api/topics/1", page_condition)
    after_expires_at = get_comments_result["expires_at"]

    print(f"comment 추가 전 잔여 시간 : {before_expires_at}")
    print(f"comment 추가 후 잔여 시간 : {after_expires_at}")
    print()
    print("-" * 50)

    # 2번 모닥불에 장작 7개 추가

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
    for i in range(1, len(dt_times)):
        time_diff = dt_times[i] - dt_times[i - 1]
        added_seconds = time_diff.total_seconds()
        minutes, seconds = divmod(added_seconds, 60)
        print(f"▶ 장작 {i}개 누적 시: 수명이 +{int(minutes)}분 {int(seconds)}초 ({int(added_seconds)}초) 연장됨")

    # 2번 모닥불의 comment 가져오기 (페이징 지원)
    page_condition = {
        "limit" : 3,
        "offset" : 0
    }
    get_comments_result = get_comments(f"{BASE_URL}/api/topics/2/", page_condition)
    print_result("get_comments", "7 ~ 2번 comment 조회", page_condition, get_comments_result)


