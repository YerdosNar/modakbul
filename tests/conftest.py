import os
import sys
import pytest
import sqlite3
from fastapi.testclient import TestClient

# Windows Console UTF-8 설정 (한글 인코딩 에러 방지)
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


# 1. 테스트용 환경 변수 우선 설정 (반드시 모듈 임포트 전 실행)
os.environ["DATABASE_URL"] = "sqlite:///./test_modakbul.db"
os.environ["SECRET_KEY"] = "test-secret-key-32bytes-for-hmac-sha256-warning"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "10"
os.environ["GARBAGE_COLLECTION_INTERVAL"] = "1" # 빠른 테스트용
os.environ["BASE_MINUTES"] = "10.0"
os.environ["DECAY_RATE"] = "0.90"
os.environ["SIMILARITY_THRESHOLD"] = "0.75"

# 프로젝트 루트 경로를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from db.init_db import init_db
from core.config import settings

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """테스트 세션 전체에서 사용할 임시 테스트용 데이터베이스를 초기화하고 teardown 시 삭제합니다."""
    # 테스트 전용 DB 파일 설정 확인
    assert settings.DB_FILENAME == "test_modakbul.db"
    
    # DB 초기화
    init_db()
    
    yield
    
    # 테스트 종료 후 테스트 DB 파일 영구 제거
    if os.path.exists(settings.DB_FILENAME):
        os.remove(settings.DB_FILENAME)
        
    # WAL 모드 관련 서브 파일(journal, shm, wal)도 함께 정리
    for suffix in ["-shm", "-wal", "-journal"]:
        side_file = settings.DB_FILENAME + suffix
        if os.path.exists(side_file):
            os.remove(side_file)

@pytest.fixture(autouse=True)
def clear_database_tables():
    """각 테스트 케이스가 격리된 상태에서 수행될 수 있도록 실행 전 모든 테이블의 데이터를 비웁니다."""
    # conftest 실행 전 DB 생성을 보장하기 위함
    conn = sqlite3.connect(settings.DB_FILENAME)
    cursor = conn.cursor()
    
    # 외래 키 무시 처리 후 모든 데이터 비우기
    cursor.execute("PRAGMA foreign_keys = OFF")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM topics")
    cursor.execute("DELETE FROM comments")
    cursor.execute("DELETE FROM topic_similarities")
    cursor.execute("DELETE FROM ash_topics")
    cursor.execute("DELETE FROM ash_comments")
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    conn.close()

class LoggingTestClient(TestClient):
    """API 호출 시 전송한 Request Payload와 수신한 Response Body/Status를 자동으로 실시간 로깅하는 테스트 클라이언트입니다."""
    
    def request(self, method: str, url: str, **kwargs):
        # 1. 요청 Payload 분석 및 로깅
        json_data = kwargs.get("json")
        form_data = kwargs.get("data")
        
        payload_desc = ""
        if json_data:
            payload_desc = f" | Payload(JSON): {json_data}"
        elif form_data:
            payload_desc = f" | Payload(Form): {form_data}"
            
        print(f"\n      [API REQ]  {method} {url}{payload_desc}")
        
        # 2. 실제 API 호출 수행
        response = super().request(method, url, **kwargs)
        
        # 3. 응답 결과 분석 및 로깅
        try:
            resp_body = response.json()
        except Exception:
            resp_body = response.text
            
        # 출력 가독성을 위해 응답 바디가 길 경우 100자로 잘라서 축약 출력
        body_summary = str(resp_body)
        if len(body_summary) > 100:
            body_summary = body_summary[:100] + "... (truncated)"
            
        print(f"      [API RESP] Status: {response.status_code} | Body: {body_summary}")
        return response

@pytest.fixture
def client():
    """테스트용 API 실시간 로깅 기능이 내장된 TestClient 객체를 반환합니다."""
    with LoggingTestClient(app) as test_client:
        yield test_client



def get_category(nodeid: str) -> str:
    """테스트 경로를 기반으로 카테고리를 분류합니다."""
    file_path = nodeid.replace("\\", "/")
    if "tests/core/" in file_path:
        return "CORE UNIT"
    elif "tests/scenarios/" in file_path:
        return "SCENARIO"
    else:
        return "INTEGRATION"


def pytest_runtest_setup(item):
    """각 테스트 케이스 실행 셋업 단계에서 한글 설명(docstring)을 터미널에 출력합니다.
    테스트 파일 경로를 파싱하여 [CORE UNIT], [INTEGRATION], [SCENARIO] 카테고리 태그를 자동으로 부여합니다.
    """
    doc = item.obj.__doc__
    if doc:
        first_line = doc.strip().split("\n")[0]
        nodeid = item.nodeid
        
        # 파일 경로 및 함수명 추출
        parts = nodeid.replace("\\", "/").split("::")
        func_name = parts[1] if len(parts) > 1 else ""
        
        category = get_category(nodeid)
            
        # 이전 테스트 완료(PASSED) 뒤에 logfinish에서 개행을 해주므로, 여기서는 가볍게 시작
        print(f"\n")
        print(f"======================================================================")
        print(f"  >>> [{category} TEST] : {func_name}")
        print(f"    - 검증 시나리오: {first_line}")
        print(f"======================================================================", end="", flush=True)


def pytest_runtest_logfinish(nodeid, location):
    """각 테스트 프로토콜이 완전히 종료된 시점(터미널에 PASSED가 출력된 직후)에 개행을 주어 다음 테스트 식별자와의 간격을 벌립니다."""
    print("\n\n\n", end="", flush=True)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """테스트 세션 종료 시, 각 카테고리별로 몇 개의 테스트 중 몇 개가 성공했는지 요약 통계를 아름답게 출력합니다."""
    passed = terminalreporter.stats.get('passed', [])
    failed = terminalreporter.stats.get('failed', [])
    skipped = terminalreporter.stats.get('skipped', [])
    error = terminalreporter.stats.get('error', [])
    
    test_results = {}
    
    for r in passed:
        if getattr(r, 'when', None) == 'call':
            test_results[r.nodeid] = 'passed'
    for r in failed:
        test_results[r.nodeid] = 'failed'
    for r in skipped:
        test_results[r.nodeid] = 'skipped'
    for r in error:
        if r.nodeid not in test_results:
            test_results[r.nodeid] = 'error'
            
    categories = {
        "CORE UNIT": {"passed": 0, "failed": 0, "skipped": 0, "error": 0},
        "INTEGRATION": {"passed": 0, "failed": 0, "skipped": 0, "error": 0},
        "SCENARIO": {"passed": 0, "failed": 0, "skipped": 0, "error": 0},
    }
    
    for nodeid, status in test_results.items():
        cat = get_category(nodeid)
        if cat in categories:
            categories[cat][status] += 1
            
    total_passed = sum(c['passed'] for c in categories.values())
    total_failed = sum(c['failed'] for c in categories.values())
    total_skipped = sum(c['skipped'] for c in categories.values())
    total_error = sum(c['error'] for c in categories.values())
    total_tests = total_passed + total_failed + total_skipped + total_error
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
    
    # 터미널에 요약 통계 출력
    terminalreporter.write_sep("=", "MODAKBUL TEST SUMMARY STATISTICS", bold=True)
    terminalreporter.write_line(f" {'Category':<15} | {'Passed':^8} | {'Failed':^8} | {'Skipped':^8} | {'Error':^8} | {'Total':^8}")
    terminalreporter.write_line("-" * 70)
    for cat, stats in categories.items():
        cat_total = sum(stats.values())
        terminalreporter.write_line(f" {cat:<15} | {stats['passed']:^8} | {stats['failed']:^8} | {stats['skipped']:^8} | {stats['error']:^8} | {cat_total:^8}")
    terminalreporter.write_line("-" * 70)
    terminalreporter.write_line(f" {'TOTAL':<15} | {total_passed:^8} | {total_failed:^8} | {total_skipped:^8} | {total_error:^8} | {total_tests:^8}")
    terminalreporter.write_line("-" * 70)
    terminalreporter.write_line(f" Success Rate: {success_rate:.1f}% ({total_passed}/{total_tests} passed)")
    terminalreporter.write_sep("=", bold=True)
