# 🪵 모닥불 (Modakbul) 요구사항 명세서

**버전:** 1.1.0  
**최근 수정일:** 2026-06-07  
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
    - ID, Password, Nickname이 누락 없이 입력되어야 한다. (빈 공백 문자만 입력 시 가입을 차단한다.)
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
    - 올바른 자격 증명 시, 서버는 인증 토큰(JWT)을 발급하여 반환한다.

**US-03** : 사용자는 로그인된 계정을 로그아웃할 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 서비스에서 안전하게 로그아웃하여
    - So that : 내 기기나 환경에서 다른 사람이 내 계정을 도용하지 못하도록 보호할 수 있다.
- Acceptance Criteria:
    - JWT 기반 무상태 토큰 형식이므로 클라이언트에게 토큰 삭제를 유도하는 성공 응답(200 OK)을 반환한다.

---

### Epic 2: 모닥불(게시물) 관리
- Goal: 사용자가 핫이슈를 생산하고, 살아있는 이슈의 피드를 조회한다.

**US-04** : 사용자는 새로운 모닥불(Topic)을 피울 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 새로운 주제나 이슈를 텍스트로 작성하여
    - So that : 사람들의 관심과 반응을 모을 수 있다.
- Acceptance Criteria:
    - 서버는 요청 시 인증된 사용자인지 검증해야 하며, 미인증 시 요청을 차단한다.
    - 입력값은 빈 문자열이거나 공백으로만 이루어질 수 없으며, 길이제한을 만족해야 한다.
    - 게시물 저장 시, 작성자의 User ID를 외래키로 함께 매핑하고, 128차원 시맨틱 임베딩 벡터를 계산하여 함께 저장한다.
    - 초기 상태값으로 적절한 만료일(예: 생성 후 +1시간)을 자동 설정한다.

**US-05** : 사용자는 현재 가장 뜨거운 모닥불 피드(전체 목록)를 볼 수 있다.
- Description:
    - As a : 비로그인 방문자를 포함한 모든 사용자
    - I want to : 살아있는 게시물 목록을 확인하여
    - So that : 현재 사람들이 가장 많이 다루는 이슈가 무엇인지 알 수 있다.
- Acceptance Criteria:
    - 로그인 여부와 상관없이 누구나 조회(GET)할 수 있어야 한다.
    - 만료일시가 지나지 않은 데이터(`is_ash = 0` 및 `expires_at > now`)만 필터링하여 반환하며, 지연 삭제 로직을 적용한다.
    - 한 번에 반환하는 게시물의 수는 기본 20개이며 limit/offset 파라미터 페이징을 지원한다.

**US-06** : 사용자는 특정 모닥불의 상세 내용과 장작들을 볼 수 있다.
- Description:
    - As a : 비로그인 방문자를 포함한 모든 사용자
    - I want to : 특정 모닥불에 달린 댓글 목록을 함께 조회하여
    - So that : 다른 사람들의 구체적인 반응을 읽고 흐름을 파악할 수 있다.
- Acceptance Criteria:
    - 활성 모닥불뿐만 아니라 이미 만료되어 아카이브 테이블(`ash_topics`)로 이관된 과거 모닥불에 대해서도 상세 조회를 허용하되, 만료된 대상은 응답에 `is_ash = 1` 상태를 마킹하여 반환한다.
    - 활성/아카이브 모두에서 찾을 수 없는 ID의 경우 404 Not Found를 반환한다.
    - 상세 정보에 포함된 댓글(장작) 목록도 페이징 조회를 지원한다.

---

### Epic 3: 장작(댓글) 관리 및 활동 정보
- Goal: 사용자가 기존 모닥불에 참여하여 의견을 남기고 수명을 연장시키며, 유저의 활동 내역을 확인한다.

**US-07** : 사용자는 모닥불에 장작(Comment)을 넣어 불씨를 살릴 수 있다.
- Description:
    - As a : 로그인한 회원
    - I want to : 특정 게시물에 댓글을 달아
    - So that : 의견을 나누고 해당 모닥불이 꺼지지 않게 수명을 연장할 수 있다.
- Acceptance Criteria (인수 조건):
    - 서버는 요청 시 인증된 사용자인지 검증해야 한다.
    - 이미 재가 되었거나 만료된 모닥불(`is_ash = 1` 또는 만료시각 경과)에는 댓글 작성을 거부(403 Forbidden)해야 한다.
    - 댓글 등록 즉시 가변 연소율 및 산소 감쇠 공식을 적용하여 수명을 연장하고, 댓글 목록에 반영한다.

**US-08** : 사용자는 특정 유저의 공개 프로필 및 최근 활동 내역을 통합 조회할 수 있다.
- Description:
    - As a : 모든 사용자
    - I want to : 특정 사용자의 기본 정보와 그 사용자가 쓴 최근 모닥불 및 장작 목록을 조회하여
    - So that : 해당 사용자의 최근 관심사와 활동 흐름을 파악할 수 있다.
- Acceptance Criteria:
    - 가입되지 않은 사용자의 ID 조회 시 404 Not Found를 반환한다.
    - 성공 시 유저 정보 요약과 함께 최근 작성한 모닥불 목록, 댓글 목록을 하나의 결과로 응답한다.

---

## 2. System Stories (Technical Specification)

### Epic 1: 사용자 인증 및 권한 (Auth)

**SYS-01** : 사용자 회원가입 API 및 암호화 처리
- `POST /api/auth/signup` 엔드포인트를 구현하고, Pydantic으로 입력 형식을 검증한다.
- `username` 컬럼에 UNIQUE 제약 조건을 설정하고, 중복 가입 시 409 Conflict 에러를 반환한다.
- 비밀번호는 `bcrypt` 라이브러리를 통해 안전하게 해싱하여 DB `password_hash` 필드에 저장한다.

**SYS-02** : 로그인 인증 및 토큰 발급
- `POST /api/auth/login` 엔드포인트를 통해 사용자 자격 증명(ID/PW)을 검증한다.
- 일치하지 않을 경우 401 Unauthorized를 반환하며, 일치할 경우 JWT 액세스 토큰을 발급한다.

**SYS-03** : 로그아웃 및 회원 탈퇴
- `POST /api/auth/logout`: 클라이언트 측의 토큰 삭제를 유도하기 위한 성공 응답을 제공한다.
- `DELETE /api/auth/me`: 현재 로그인한 회원의 탈퇴 처리를 수행한다. 비밀번호 재확인을 거쳐 불일치 시 401을 반환하고, 일치 시 DB에서 계정을 영구 삭제한다. DB `ON DELETE CASCADE` 제약 조건에 의해 연관 모닥불 및 댓글도 함께 삭제된다.

---

### Epic 2: 모닥불(게시물) 관리

**SYS-04** : 모닥불 생성, 시맨틱 분석 및 초기 수명 부여
- `POST /api/topics/`를 통해 신규 모닥불을 개설한다.
- 모닥불 생성 시 문장 텍스트에서 128차원 L2 정규화 유닛 벡터(가상 임베딩)를 추출해 JSON 문자열로 데이터베이스에 저장한다.
- 생성 즉시 다른 활성 모닥불들과의 코사인 유사도를 계산하여 `SIMILARITY_THRESHOLD` 이상인 대상을 `topic_similarities` 테이블에 매핑 저장한다.
- 초기 수명(`expires_at`)은 생성 시간 기준 `now + 1시간`으로 설정한다.

**SYS-05** : 지연 삭제 필터링 및 피드 페이징
- `GET /api/topics/` 호출 시 `expires_at > now AND is_ash = 0` 조건을 SQL 쿼리에 적용하여 유효한 데이터만 필터링 조회한다.
- `GET /api/topics/ashes` 호출 시 이미 만료되었거나 아카이브 테이블(`ash_topics`)로 이관된 과거 모닥불 피드를 UNION ALL 쿼리를 통해 효율적으로 결합 조회한다.

**SYS-06** : 모닥불 상세 정보 및 아카이브 조인
- `GET /api/topics/{topic_id}` 호출 시 활성 테이블(`topics`)과 아카이브 테이블(`ash_topics`)을 순차 대조하여 단건 데이터를 식별한다.
- 해당 모닥불이 아카이브되었거나 만료 상태인 경우 하위 댓글 조회를 아카이브 댓글 테이블(`ash_comments`)에서 수행하고, 응답 데이터에 `is_ash = 1`을 세팅한다.

---

### Epic 3: 장작(댓글) 관리 및 시스템 유지보수

**SYS-07** : 장작 추가 및 산소 감쇠 가변 연소율 시스템 적용
- `POST /api/topics/{topic_id}/comments` 호출 시 댓글 생성과 부모 모닥불의 수명 연장을 단일 데이터베이스 트랜잭션으로 처리한다.
- **가변 연소율 공식:** 누적 댓글 수(`comment_count`)가 많아질수록 추가 시간은 지수적으로 감쇠된다.
  $$\text{extension\_seconds} = \text{BASE\_MINUTES} \times 60 \times (\text{DECAY\_RATE}^{\text{comment\_count}})$$
- **산소 경쟁 시스템:** 시맨틱적으로 유사한(코사인 유사도 $\ge$ `SIMILARITY_THRESHOLD`) 주변 활성 모닥불들의 댓글 수 합산(`near_comments_sum`)에 비례해 산소 밀도 계수를 차등 적용한다.
  $$\text{oxygen\_factor} = \max(0.3, 1.0 - (\text{near\_comments\_sum} \times 0.05))$$
- 최종 수명 연장 시간은 아래와 같으며, 데이터 폭증 방지를 위해 최소 하한선을 10초로 제한한다.
  $$\text{final\_seconds} = \max(10.0, \text{extension\_seconds} \times \text{oxygen\_factor})$$

**SYS-08** : 2단계 청크 가비지 컬렉션 (Garbage Collection)
- **1단계 (논리 잠금):** 만료 시각이 도래한 모든 모닥불의 `is_ash`를 1로 변경한다. (초고속 인덱스 업데이트, 즉시 추가 댓글 방어)
- **2단계 (물리 청크 이관 및 쓰로틀링):** `is_ash = 1`인 대상들을 `ARCHIVE_BATCH_SIZE` 크기 단위로 쪼개어 읽은 후 아카이브 테이블(`ash_topics`, `ash_comments`)로 안전하게 복사하고 활성 테이블에서 물리 삭제한다. 각 배치 루프 사이에 `ARCHIVE_THROTTLE_INTERVAL` 휴식 시간을 두어 SQLite 락 점유를 일시 양보한다.

**SYS-09** : SQLite WAL 모드 지원 및 유효성 검사 강화
- 데이터베이스 초기화 시 `PRAGMA journal_mode = WAL` 설정을 주입해 파일 쓰기 동시성 한계를 극복한다.
- 모든 API 요청 데이터에 대해 앞뒤 공백을 제거(`strip()`)하고 빈 문자열 여부를 검사하는 유효성 레이어를 강화한다.

---

## 3. 기술 스택 (Tech Stack)

- **Language:** Python 3.10.20
- **Framework:** FastAPI
- **Database:** SQLite3 (WAL 모드 활성화)
- **DB Access:** Python `sqlite3` 내장 모듈 (Raw SQL 작성)
- **Authentication:** passlib[bcrypt], PyJWT (JWT 무상태 토큰 인증)
- **Background Scheduler:** APScheduler (2단계 백그라운드 아카이브 수집 스케줄러)
- **Testing Tools:** pytest, httpx

---

## 4. 디렉토리 구조 (Directory Structure)
```
modakbul/
├── main.py                 # FastAPI 진입점 및 APScheduler 등록
├── api/                    # API 엔드포인트 계층 (Routers)
│   ├── dependencies.py     # 인증 토큰 주입 등 공통 의존성 (Depends)
│   └── routers/
│       ├── auth.py         # 로그인/가입/탈탈퇴 엔드포인트
│       ├── topics.py       # 모닥불 생성 및 피드 조회 엔드포인트
│       ├── comments.py     # 장작 추가 엔드포인트
│       └── users.py        # 유저 통합 프로필 엔드포인트
├── services/               # 비즈니스 로직 계층 (Service Layer)
│   ├── auth_service.py     # 비밀번호 암호화 대조 및 토큰 발급 로직
│   ├── topic_service.py    # 유사도 연산 및 피드 포매팅 로직
│   ├── comment_service.py  # 산소 감쇠 및 가변 연소율 시간 연장 계산 로직
│   └── user_service.py     # 유저 프로필 및 최근 활동 취합 비즈니스 로직
├── repositories/           # 데이터 액세스 계층 (Repository Layer)
│   ├── auth_repository.py  # 유저 조회/생성/삭제 SQL
│   ├── topic_repository.py # 모닥불 조회/삽입 및 유사도 일괄 등록 SQL
│   ├── comment_repository.py # 장작 삽입 및 주변 유사 장작수 집계 SQL
│   └── user_repository.py  # 유저 정보 및 유저별 최근 글/댓글 조회 SQL
├── schemas/                # Pydantic 데이터 검증 DTO 모델
│   ├── auth.py             # 회원가입/탈퇴/로그인 모델
│   ├── topics.py           # 모닥불 요청/응답 모델
│   ├── comments.py         # 장작 요청/응답 모델
│   └── users.py            # 통합 유저 프로필 응답 모델
├── db/                     # DB 연결 및 기초 테이블 스키마 정의
│   ├── connection.py       # 커넥션 풀 및 컨텍스트 매니저
│   └── init_db.py          # WAL 설정 및 테이블 신규 스키마 빌드 스크립트
├── core/                   # 핵심 설정 및 유틸 알고리즘
│   ├── config.py           # 환경변수 로드 및 상수 세팅
│   ├── exceptions.py       # 글로벌 에러 핸들러 연계 커스텀 예외 정의
│   ├── burn_rate.py        # 가변 연소율 및 스팸 방지 하한 수식 계산기
│   ├── similarity.py       # Cosine Similarity 유닛 연산 함수
│   └── embedding_utils.py  # 128차원 가상 시맨틱 벡터 생성기
├── jobs/                   # 백그라운드 스케줄러 정의
│   └── scheduler.py        # 2단계 아카이브 이관 가비지 컬렉터 정의
└── tests/                  # pytest 기반 격리 테스트 스위트
```