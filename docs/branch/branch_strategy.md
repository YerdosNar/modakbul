# 🌳 모닥불(Modakbul) 브랜치 및 협업 전략 (Branch Strategy)

본 문서는 **Git Merge Conflict(충돌) 최소화 개발**을 진행하기 위한 브랜치 전략과 역할 분담 가이드입니다.

---

## 1. 브랜치 기본 구조 (Base Branches)

* **`master`** : 언제든 배포 및 시연이 가능한 프로덕션(Production) 브랜치
* **`develop`** : 기능 개발이 완료될 때마다 병합(Merge)하여 테스트하는 통합 브랜치
* **`feat/...`** : 각 팀원들이 기능 개발을 위해 파생시키는 작업 브랜치 (작업 완료 후 `develop`으로 PR)
* **`fix/...`** : 버그 수정을 위한 전용 브랜치
* **`refactor/...`** : 코드 구조 개선을 위한 전용 브랜치 (예: Service/Repository 패턴 도입 등)

---

## 2. 단계별 개발 시나리오 및 역할 분담

Git 충돌을 원천 차단하기 위해, 개발은 철저히 **3단계(Phase)**로 나누어 진행하며, 팀원들은 **자신에게 할당된 폴더/파일만 수정**하는 것을 원칙으로 합니다.

### Phase 0: 프로젝트 초기 뼈대 설정
동시 개발 시 파일 이름이나 데이터 구조가 달라 발생하는 충돌을 막기 위해, 코어 아키텍처 담당자가 기본 뼈대(인터페이스)를 먼저 구축하고 병합합니다.

* **Branch:** `develop`
* **담당자:** 차경호
* **작업 내용:**
  * `main.py` (FastAPI 앱 초기화)
  * `db/init_db.py` (CREATE TABLE 쿼리 및 WAL 설정)
  * `schemas/*.py` (Pydantic 입출력 데이터 DTO 폼 - **[중요] API와 비즈니스/DB 레이어 간의 계약서 역할**)
  * `services/` 및 `repositories/` (함수명, 매개변수, Return 타입만 선언하고 내부는 `pass`로 둔 빈 스켈레톤 함수 작성)

---

### ⚡ Phase 1: 4인 병렬 개발 (동시 진행)
모든 팀원은 최신 `develop`을 `pull` 받은 뒤 각자의 브랜치를 생성하여 동시 개발을 시작합니다.

#### 🧱 [Service & Repository 개발]
> **Rule:** 본인 담당 도메인의 `services/` 및 `repositories/` 폴더 내 파일만 수정 가능.

| 담당자 | 브랜치명 | 전담 작업 파일 | 주요 구현 로직 |
| :--- | :--- | :--- | :--- |
| **김건우** | `feat/comment` | `services/comment_service.py`<br>`repositories/comment_repository.py` | - 장작 추가 단일 트랜잭션<br>- 산소 감쇠 및 가변 연소율 연산 연동 |
| **나르지기토브 예르도스** | `feat/topic` | `services/topic_service.py`<br>`repositories/topic_repository.py` | - 모닥불 생성 및 코사인 유사도 일괄 매핑<br>- 지연 삭제 필터링 활성 피드 구현 |
| **차경호** | `feat/auth` | `services/auth_service.py`<br>`repositories/auth_repository.py` | - 유저 암호화 회원가입/로그인/탈퇴 로직<br>- JWT 토큰 인가 검증 미들웨어 |
| **전상준** | `feat/setting` | `core/config.py`<br>`db/connection.py` | - 공통 환경 설정 관리 및 커넥션 관리 |

---

### 🧩 Phase 2: 시스템 통합 및 최적화
모든 Phase 1 브랜치가 `develop`에 병합되고 API 연동 테스트가 성공하면, 남은 스케줄러 작업 및 예외 처리 고도화를 마무리합니다.

* **Branch:** `feat/garbage-collect`, `feat/users-domain`
* **작업 파일:** `jobs/scheduler.py`, `services/user_service.py`, `repositories/user_repository.py`, `api/routers/users.py`
* **주요 구현 로직:** 
  * 1단계 논리 잠금 및 2단계 쓰로틀링 배치 청크 이관을 수행하는 백그라운드 가비지 컬렉터(GC) 스케줄러 구현.
  * 신규 유저 도메인(통합 프로필 조회 API) 설계 및 통합.

---

## 🚨 팀원 필독: Git 충돌 방지 절대 수칙

1. **내 구역 준수:** 할당된 폴더와 파일 이외의 코드는 절대 건드리지 않습니다. (예: API Router 담당자는 Service 코드가 어떻게 생겼는지 내부 구현에 직접 개입하지 말고, 인터페이스 규격에 맞춰 호출만 진행해야 합니다.)
2. **Pull 생활화:** 작업 시작 전과 Commit 전에 항상 `develop` 브랜치를 `pull` 받아서 최신 상태를 유지하세요.
3. **Pydantic DTO는 법이다:** `schemas/` 에 정의된 데이터 형태를 함부로 바꾸지 마세요. 수정이 필요하면 반드시 팀원과 사전 합의 후 변경해야 합니다.
4. **테스트 격리 규정 준수:** 로컬 테스트 시에는 `test_modakbul.db` 파일이 임시 생성 및 제거되도록 `conftest.py` 설정을 위반하지 않아야 합니다.