# 🌳 모닥불(Modakbul) 브랜치 및 협업 전략 (Branch Strategy)

본 문서는 **Git Merge Conflict(충돌) 최소화 개발**을 진행하기 위한 브랜치 전략과 역할 분담 가이드입니다.

---

## 1. 브랜치 기본 구조 (Base Branches)

* **`main`** : 언제든 배포 및 시연이 가능한 프로덕션(Production) 브랜치
* **`develop`** : 기능 개발이 완료될 때마다 병합(Merge)하여 테스트하는 통합 브랜치
* **`feat/...`** : 각 팀원들이 기능 개발을 위해 파생시키는 작업 브랜치 (작업 완료 후 `develop`으로 PR)

---

## 2. 단계별 개발 시나리오 및 역할 분담

Git 충돌을 원천 차단하기 위해, 개발은 철저히 **3단계(Phase)**로 나누어 진행하며, 팀원들은 **자신에게 할당된 폴더/파일만 수정**해야 합니다.

### Phase 0: 프로젝트 초기 뼈대 설정
동시 개발 시 파일 이름이나 데이터 구조가 달라 발생하는 충돌을 막기 위해, 코어 아키텍처 담당자가 기본 뼈대(인터페이스)를 먼저 구축하고 병합합니다.

* **Branch:** `develop`
* **담당자:** 경호
* **작업 내용:**
  * `main.py` (FastAPI 앱 초기화)
  * `db/init_db.py` (CREATE TABLE 쿼리 및 ERD)
  * `schemas/*.py` (Pydantic 입출력 데이터 폼 - **[중요] 이후 API 팀과 DB 팀의 계약서 역할**)
  * `crud/*.py` (함수명, 매개변수, Return 타입만 선언하고 내부는 `pass`로 둔 빈 껍데기 함수 작성)

---

### ⚡ Phase 1: 4인 병렬 개발 (동시 진행)
모든 팀원은 최신 `develop`을 `pull` 받은 뒤 각자의 브랜치를 생성하여 동시 개발을 시작합니다.

#### 🗄️ [DB 팀] 생쿼리 및 비즈니스 로직
> **Rule:** `crud/` 폴더 및 `core/` 폴더 내의 파일만 수정 가능.

| 담당자 | 브랜치명 | 전담 작업 파일 | 주요 구현 로직 |
| :--- | :--- | :--- | :--- |
| **경호** | `feat/db-core` | `crud/topics.py`<br>`crud/comments.py` | - 지연 삭제(`WHERE expires_at > now`) 피드 조회<br>- 가변 연소율 시간 계산 알고리즘<br>- 장작 추가 단일 트랜잭션(`INSERT` & `UPDATE`) |
| **?** | `feat/db-auth` | `crud/auth.py`<br>`core/security.py` | - 유저 생성 및 단방향 암호화(`bcrypt`) 쿼리<br>- JWT 토큰 발급 및 검증 로직 구현 |

#### 🌐 [API 팀] 라우터 및 미들웨어
> **Rule:** `api/` 폴더 내의 파일만 수정 가능. (`crud` 함수는 껍데기만 호출하여 사용)

| 담당자 | 브랜치명 | 전담 작업 파일 | 주요 구현 로직 |
| :--- | :--- | :--- | :--- |
| **?** | `feat/api-auth-topic` | `api/routers/auth.py`<br>`api/routers/topics.py` | - 회원가입/로그인 API 엔드포인트 구현<br>- 모닥불 생성 및 피드 조회(LIMIT/OFFSET 파라미터 처리) 연결 |
| **?** | `feat/api-comment-deps` | `api/routers/comments.py`<br>`api/dependencies.py` | - 장작 추가 API 엔드포인트 구현<br>- `Depends()`용 토큰 검증 및 로그인 유저 식별 공통 함수 구현 |

---

### 🧩 Phase 2: 시스템 통합 및 최적화
모든 Phase 1 브랜치가 `develop`에 병합되고 API 연동 테스트가 성공하면, 남은 백그라운드 작업을 마무리합니다.

* **Branch:** `feat/system-scheduler`
* **작업 파일:** `jobs/scheduler.py`, `main.py`
* **주요 구현 로직:** * APScheduler를 활용하여 `expires_at < now` 인 만료 모닥불 데이터를 DB에서 물리적으로 하드 딜리트(Hard Delete)하는 주기적 작업 구축.

---

## 🚨 팀원 필독: Git 충돌 방지 절대 수칙

1. **내 구역 준수:** 할당된 폴더와 파일 이외의 코드는 절대 건드리지 않습니다. (예: API 팀은 `crud` 코드가 어떻게 생겼는지 신경 쓰지 말고, 정해진 `schemas` 대로 데이터만 넘기세요.)
2. **Pull 생활화:** 작업 시작 전과 Commit 전에 항상 `develop` 브랜치를 `pull` 받아서 최신 상태를 유지하세요.
3. **Pydantic은 법이다:** `schemas/` 에 정의된 데이터 형태를 함부로 바꾸지 마세요. 수정이 필요하면 반드시 팀원과 합의 후 변경해야 합니다.