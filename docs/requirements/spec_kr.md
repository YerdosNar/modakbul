# 🪵 모닥불 (Modakbul) 요구사항 명세서

**버전:** 1.0.0  
**최근 수정일:** 2026-04-11
**프로젝트 성격:** 실시간 휘발성 익명 커뮤니티 백엔드 API

---

## 1. User Stories

### Epic 1: 사용자 인증 및 권한 (Auth)
- Goal: 방문자가 회원가입을 하고 로그인하여 서비스의 인증된 사용자가 된다.

**US-01** : 사용자는 서비스에 회원가입을 할 수 있다.
- Description:
    - As a : 방문자
    - I want to : ID와 Password 등의 정보를 입력하여 회원가입을 하여
    - So that : 자신만의 계정을 생성하고 모닥불 서비스에 참여할 수 있다.
- Acceptance Criteria:
    - ID, Password, Nickname이 누락 없이 입력되어야 한다.
    - 이미 존재하는 아이디로 가입 시도 시, 409 Conflict 에러를 반환한다.
    - 비밀번호는 DB에 평문으로 저장되지 않고 해싱(예: bcrypt) 처리되어야 한다.
    - 성공 시 201 Created와 함께 가입 완료 응답을 반환한다.

**US-02** : 사용자는 생성한 계정으로 로그인을 할 수 있다.
- Description:
    - AS a : 가입된 회원
    - I want to : 본인의 계정 정보로 로그인하여
    - So that : 모닥불 피우기, 장작 넣기 등의 인증된 사용자 권한을 얻을 수 있다.
- Acceptance Criteria:
    - 가입되지 않은 ID거나 Password가 틀릴 경우, 401 Unauthorized를 반환한다.
    - 올바른 자격 증명 시, 서버는 인증 토큰(또는 세션)을 발급하여 반환한다.

**US-03** : 사용자는 로그인된 계정을 로그아웃할 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 서비스에서 안전하게 로그아웃하여
    - So that : 내 기기나 환경에서 다른 사람이 내 계정을 도용하지 못하도록 보호할 수 있다.
- Acceptance Criteria:
    - 서버는 클라이언트의 인증 토큰(또는 세션)을 무효화 처리한다.
    - 성공적으로 처리되면 200 OK 응답을 반환한다.

### Epic 2: 모닥불(게시물) 관리
- Goal: 사용자가 핫이슈를 생산하고, 살아있는 이슈의 피드를 조회한다.

**US-04** : 사용자는 새로운 모닥불(Topic)을 피울 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 새로운 주제나 이슈를 텍스트로 작성하여
    - So that : 사람들의 관심과 반응을 모을 수 있다.
- Acceptance Criteria:
    - 서버는 요청 시 인증된 사용자인지 검증해야 하며, 미인증 시 요청을 차단한다.
    - 게시물 저장 시, 작성자의 User ID를 외래키로 함께 매핑하여 저장한다.
    - 초기 상태값으로 적절한 만료일(예: 생성 후 +1시간)을 자동 설정한다.

**US-05** : 사용자는 현재 가장 뜨거운 모닥불 피드(전체 목록)를 볼 수 있다.
- Description:
    - As a : 비로그인 방문자를 포함한 모든 사용자
    - I want to : 살아있는 게시물 목록을 확인하여
    - So that : 현재 사람들이 가장 많이 다루는 이슈가 무엇인지 알 수 있다.
- Acceptance Criteria:
    - 로그인 여부와 상관없이 누구나 조회(GET)할 수 있어야 한다.
    - 만료일시가 지나지 않은 데이터만 필터링하여 반환하며, 지연 삭제 로직을 적용한다.
    - 남은 수명이 긴 순서대로 정렬하여 반환한다.
    - 한 번에 반환하는 게시물의 수(예: 20개)를 제한하거나 페이징(커서/오프셋) 처리하여 반환한다.

**US-06** : 사용자는 특정 모닥불의 상세 내용과 장작들을 볼 수 있다.
- Description:
    - As a : 비로그인 방문자를 포함한 모든 사용자
    - I want to : 특정 모닥불에 달린 댓글 목록을 함께 조회하여
    - So that : 다른 사람들의 구체적인 반응을 읽고 흐름을 파악할 수 있다.
- Acceptance Criteria:
    - 만료일시가 지난 게시물의 ID로 접근 시 404 Not Found 또는 403 Forbidden을 반환한다.
    - 유효한 게시물일 경우, 본문 데이터와 함께 해당 모닥불에 속한 댓글 리스트를 반환한다.


### Epic 3: 장작(댓글) 관리
- Goal: 사용자가 기존 모닥불에 참여하여 의견을 남기고 수명을 연장시킨다.

**US-7** : 사용자는 모닥불에 장작(Comment)을 넣어 불씨를 살릴 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 특정 게시물에 댓글을 달아
    - So that : 의견을 나누고 해당 모닥불이 꺼지지 않게 수명을 연장할 수 있다.
- Acceptance Criteria (인수 조건):
    - 서버는 요청 시 인증된 사용자인지 검증해야 한다.
    - 댓글 저장 시, 작성자의 User ID와 속한 모닥불의 Topic ID를 모두 매핑한다.
    - 이미 만료일이 지난 모닥불에는 댓글 작성을 거부(404/403)해야 한다.
    - 댓글 저장 성공 즉시 만료일을 연장하되, 모닥불에 누적된 댓글 수에 따라 가변 연소율을 적용하여 연장되는 시간을 점진적으로 감소시킨다. (상세 공식은 System Story 참조.)

---

## 2. System Stories (Technical Specification)

### Epic 1: 사용자 인증 및 권한 (Auth)
- Goal: 백엔드 시스템에서 사용자의 신원 정보를 안전하게 검증하고 토큰 기반 인증 환경을 구축한다.

**SYS-01** : 사용자 회원가입 API 및 암호화 처리
- Description:
    - As a : 백엔드 서버
    - I want to : 사용자 회원가입 요청을 받아 비밀번호를 단방향으로 안전하게 암호화하여 저장하여
    - So that : 계정 정보 유출을 방지하고 데이터 무결성을 보장할 수 있다.
- Acceptance Criteria:
    - `POST /api/auth/signup` 엔드포인트를 구현하여 누락된 입력값을 검증한다.
    - DB의 `users` 테이블 `username` 컬럼에 UNIQUE 제약 조건을 설정하여 중복 가입을 DB 스키마 레벨에서 차단하고 409 Conflict 에러를 반환한다.
    - 입력받은 Password는 평문으로 저장하지 않고 반드시 `bcrypt`를 이용해 해싱 처리하여 저장한다.
    - 처리 성공 시 201 Created 응답을 반환한다.

**SYS-02** : 로그인 인증 및 토큰 발급
- Description:
    - As a : 백엔드 서버
    - I want to : 로그인 자격 증명을 검증하고 JWT(또는 세션)를 발급하여
    - So that : 클라이언트가 이후의 요청에서 인증된 상태를 증명할 수 있게 한다.
- Acceptance Criteria:
    - `POST /api/auth/login` 엔드포인트를 구현하여 DB 정보와 대조한다.
    - 일치하지 않을 경우 401 Unauthorized를 반환한다.
    - 일치할 경우 서버는 접근 권한이 담긴 인증 토큰(또는 세션 ID)을 생성하여 반환한다.

**SYS-03** : 로그아웃 및 토큰 무효화
- Description:
    - As a : 백엔드 서버
    - I want to : 클라이언트의 로그아웃 요청 시 기즌 인증 토큰/세션을 무효화하여
    - So that : 인가되지 않은 비정상적인 접근을 서버 단에서 차단할 수 있다.
- Acceptance Criteria:
    - `POST /api/auth/logout` 엔드포인트를 구현한다.
    - 서버 측 세션 저장소에서 해당 세션을 삭제하거나, JWT의 경우 클라이언트 삭제 유도 및 필요시 블랙리스트 처리를 수행하여 200 OK를 반환한다.

### Epic 2: 모닥불(게시물) 관리
- Goal: 휘발성 데이터의 생성과 지연 삭제 기반의 효율적인 데이터 조회를 처리한다.

**SYS-04** : 모닥불 생성 및 초기 수명 부여
- Description:
    - As a : 시스템
    - I want to : 인증된 사용자의 게시물 생성 요청을 받아 초기 수명을 설정하고 DB에 저장하여
    - So that : 휩라성 게시물의 생명 주기를 시작할 수 있따.
- Acceptance Criteria:
    - 미들웨어 또는 의존성 주입(`Depends()`)을 통해 Controller 도달 전 토큰 유효성을 선제적으로 검증한다.
    - 데이터 삽입 시 토큰에서 추출한 User ID를 외래키로 매핑한다.
    - `expires_at` 컬럼의 기본값을 현재 서버 시간(`datetime.utcnow()`) 기준 '+1시간'으로 자동 계산하여 삽입한다.

**SYS-05** : 지연 삭제 기반 피드 조회 및 페이징
- Description:
    - As a : 시스템
    - I want to : 게시물 목록 조회 시 만료된 데이터를 쿼리 레벨에서 필터링하고 페이징 처리하여 반환하여
    - So that : 유효한 데이터만 제공하고 데이터베이스 부하 및 메모리 초과를 방지할 수 있다.
- Acceptance Criteria:
    - `GET /api/topics` 호출 시 유 쿼리에 `WHERE expires_at > 현재시간` 조건을 부여하여 논리적으로 삭제된 데이터를 제외한다.
    - 쿼리에 `ORDER BY expires_at DESC` 정렬을 적용하낟.
    - `LIMIT 20 OFFSET?` 구문을 강제하여 페이징을 구현하고, 조회 성능을 위해 `expires_at` 컬럼에 인덱스(Index)를 적용한다.

**SYS-06** : 모닥불 상세 및 연관 장작(댓글) 조인 조회
- Description:
    - As a : 시스템
    - I want to : 특정 게시물 ID 조회 시 게시물 본문과 연관된 댓글 목록을 함께 로드하고 만료 여부를 다시 검증하여
    - So that : 유효한 게시물의 상세 정보만 안전하게 조합하여 클라이언트에 제공할 수 있다.
- Acceptance Criteria:
    - `GET /api/topics/{topic_id}` 호출 시 조회된 객체의 `expires_at`이 서버 현재 시간보다 과거라면 즉시 404 또는 403 예외를 발생시킨다.
    - 유효할 경우, 모닥불 본문 데이터와 `comments` 테이블의 연관 데이터를 JOIN 또는 2중 쿼리로 로드하여 응답 객체를 반환한다.

### Epic 3: 장작(댓글) 관리 및 시스템 유지보수

**SYS-07** : 장작 추가 및 가변 연소율 알고리즘 적용
- Description:
    - As a : 시스템 (알고리즘 로직)
    - I want to : 댓글 추가 요청 시 모닥불의 누적 댓글 수에 따라 연장되는 수명 시간을 단게적으로 감소시켜
    - So that : 특정 게시물의 영구적인 생명 연장(어뷰징)을 방지하고 트랜잭션 정합성을 보장할 수 있다.
- Acceptance Criteria:
    - 댓글 INSERT 쿼리와 모닥불 테이블의 `expires_at` UPDATE 쿼리는 반드시 '단일 트랜잭션'으로 묶어 롤백 가능하도록 처리한다.
    - 댓글 등록 시, 해당 모닥불의 누적 댓글 수(`comment_count`)를 조회하여 지정된 공식(예: 0~9개 +10분, 10~49개 +5분 등)에 따라 시간을 계산하여 업데이트한다.
    - 동시성 문제(Race Condition)를 방지하기 위해 DB 레벨의 Row Lock 또는 원자적 업데이트 쿼리를 적용한다.

**SYS-08** : 물리적 가비지 컬렉터 (백그라운드 최적화)
- Description:
    - As a : 백그라운드 스케줄러
    - I want to : 주기적으로 만료된 모닥불 데이터를 물리적으로 하드 딜리트(Hard Delete)하여
    - So that : 누적된 더미 데이터로 인한 DB 용량 낭비를 막고 시스템을 쾌적하게 유지할 수 있다.
- Acceptance Criteria:
    - 백그라운드 작업(예: APScheduler 등)을 통해 주기적으로 `DELETE FROM topics WHERE expires_at < 현재시간` 쿼리를 실행한다.
    - DB 스키마 설계 시 `ON DELETE CASCADE` 옵션을 설정하여, 모닥불 삭제 시 연결된 장작(댓글) 데이터도 자동으로 일괄 삭제되도록 구성한다.


---

## 3. 기술 스택 (Tech Stack)

- **Language:** Python 3.10.20
- **Framework:** FastAPI
- **Database:** SQLite3
- **DB Access**: Python sqlite3 내장 모듈
- **Authentication** : passlib[bcrypt], PyJWT
- **IDE** VSCode
- **Version Control**: Git / Github
- **Envirionment**: Python venv

---

## 4. 디렉토리 구조 (Directory Structure)
```
modakbul_backend/
├── main.py              # FastAPI 앱 실행의 진입점 (스케줄러 시작 등)
├── api/                 # API 엔드포인트 (Router)
│   ├── dependencies.py  #   토큰 검증, 로그인 유저 식별 등 공통 함수 (Depends)
│   └── routers/
│       ├── auth.py         # POST /auth/signup, /auth/login 등
│       ├── topics.py       # GET /topics, POST /topics 등
│       └── comments.py     # POST /topics/{id}/comments 등
├── crud/                # DB 접근 & 비즈니스 로직 (Repository+Service)
│   ├── auth.py             # 유저 생성, 조회 생쿼리 
│   ├── topics.py           # 모닥불 생성, 지연 삭제 필터링 조회가 포함된 생쿼리
│   └── comments.py         # 장작 추가 및 가변 연소율 시간 계산 로직
├── schemas/             # Pydantic 데이터 검증 모델
│   ├── auth.py             # 회원가입 입력/출력 폼
│   ├── topics.py           # 모닥불 생성 입력/출력 폼
│   └── comments.py         # 장작 입력/출력 폼
├── db/                  # 데이터베이스 인프라 설정
│   ├── connection.py       # sqlite3 DB 연결 객체 반환 유틸리티
│   └── init_db.py          # CREATE TABLE 생쿼리를 모아둔 초기화 스크립트
├── core/                # 보안 및 환경 설정
│   ├── config.py           # JWT 시크릿 키, 만료 시간 등 상수 관리
│   └── security.py         # bcrypt 해싱 함수, JWT 생성 함수 등
└── jobs/                # 백그라운드 작업
    └── scheduler.py        # APScheduler (만료 모닥불 물리 삭제 로직)
```