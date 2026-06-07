# 🔥 모닥불 (Modakbul)

**2026-Spring Software Engineering Team Project**

**Instructor:** Jaekwon Lee

---

## 👨‍💻 Team Members & Roles

| Name | Role & Responsibilities | GitHub Profile |
| --- | --- | --- |
| **김건우** | comment 기능 개발, 장작 추가 및 연소율 계산 로직 개발 | [Github Profile](https://github.com/goukimesatz) |
| **나르지기토브 예르도스** | topic 기능 개발, 모닥불 생성 및 유사도 연산 로직 개발 | [Github Profile](https://github.com/YerdosNar) |
| **전상준** | setting 기능 개발, DB 연동 및 공통 설정 설계 | [Github Profile](https://github.com/nclsang) |
| **차경호** | auth, garbage-collect 기능 개발, 아키텍처 및 스케줄러 개발 | [Github Profile](https://github.com/Homeria) |

---

## 📖 Project Overview

**모닥불 (Modakbul)**은 현재 화제가 되는 이슈에 대해 실시간으로 밀도 있게 소통할 수 있는 익명 커뮤니티 백엔드 API 입니다.

모든 모닥불(Topic)은 생성 시 기본 1시간의 수명을 부여받습니다. 사용자들이 지속적으로 '장작(Comment)'을 추가하면 가변 연소율 및 산소 경쟁 알고리즘에 의해 수명이 연장되지만, 사람들의 관심이 식어 수명이 다한 게시물은 백그라운드 가비지 컬렉터에 의해 자동으로 안전하게 아카이브 테이블로 이관 후 소멸됩니다. 이를 통해 휘발성을 보장하고 언제 접속하든 지금 가장 활발하게 논의되는 신선한 주제만 남게 됩니다.

---

## 🎯 Project Vision Statement

- **Target Users:** 영구적인 디지털 발자국이 남는 것을 부담스러워하며 실시간 이슈에 대해 가볍게 소통하고 싶은 익명 사용자
- **Problem or Need:** 기존 커뮤니티는 한 번 작성된 글이 영구 보존되어 정보의 피로감과 불필요한 흔적을 남김.
- **Product Category:** 실시간 휘발성 익명 커뮤니티 API 서버.
- **Key Benefit & Differentiation:** 게시물에 '수명(expires_at)'을 부여하고, 지연 삭제(Lazy Deletion) 및 2단계 청크 아카이빙 물리 삭제를 통해 참여가 없는 게시물을 데이터베이스에서 흔적 없이 완전히 소멸시킴.

---

## 📌 Project Goals & Scope

- **Business Goals:** 가변 연소율 및 산소 감쇠 알고리즘, 트랜잭션 제어를 통한 시스템 자원 최적화 및 휘발성 데이터 처리.
- **In-Scope (Major Features):**
    - JWT 토큰 기반의 사용자 인증 및 권한 관리 (회원가입/로그인/탈퇴)
    - 모닥불(게시물) 생성 및 장작(댓글) 추가를 위한 RESTful API 구현
    - DB 쿼리(Raw SQL)를 활용한 지연 삭제(Lazy Deletion) 기반의 활성 피드 및 식은 모닥불(Ashes) 피드 조회
    - 장작 누적 개수 및 주변 모닥불 밀집도에 따라 수명 연장 시간이 점진적으로 줄어드는 '산소 경쟁 가변 연소율' 알고리즘 적용
    - 데이터베이스 동시성 충돌 방지를 위해 WAL 모드를 도입하고, 2단계 논리 잠금 및 쓰로틀링 청크 이관을 수행하는 백그라운드 가비지 컬렉터(GC)
    - 유저 프로필과 유저의 최근 글/댓글을 한 번에 가져오는 통합 프로필 API
- **Out-of-Scope:**
    - 복잡한 프론트엔드 UI/UX 구현
    - WebSocket 기반의 실시간 데이터 푸시 (조회 성능 최적화 기반의 REST API로 대체)

---

## 📅 Milestones

- **Milestone 1: 코어 아키텍처 및 공통 인터페이스 구축 (Week 1 ~ Week 2)**
    - **목표:** DB 스키마 설계 및 API-DB 팀 간의 개발 계약(Pydantic Schemas) 확정
    - **주요 작업 (Tasks):**
        - SQLite3 기반 관계형 DB 스키마 (users, topics, comments, topic_similarities, ash_topics, ash_comments) 설계 및 ERD 작성
        - 데이터 입출력 폼(Pydantic BaseModel) 정의를 통한 팀 간 독립적 개발 환경 구축
        - FastAPI 서버 초기 환경 세팅 및 라우터/의존성 주입 스켈레톤 코드 세팅
        - JWT 시크릿 키 및 단방향 암호화(bcrypt) 환경 구성
    - **산출물 (Deliverables):** DB 스키마 생성 스크립트(`init_db.py`), API/DTO 인터페이스 정의서

- **Milestone 2: 도메인별 API 및 서비스/레포지토리 순차 개발 (Week 3 ~ Week 5)**
    - **목표:** Auth, Topics, Comments, Users 도메인의 실제 비즈니스 로직 및 엔드포인트 구현
    - **주요 작업 (Tasks):**
        - **Auth:** 회원가입/로그인/회원탈퇴 및 JWT 토큰 발급/검증 미들웨어 구현
        - **Topics:** 모닥불 피우기 로직, 코사인 유사도 분석 매핑 및 지연 삭제 필터링이 적용된 활성/식은(Ashes) 피드 조회 쿼리 구현
        - **Comments:** 단일 트랜잭션을 적용한 장작 추가 및 산소 경쟁 가변 연소 수명 연장 알고리즘 구현
        - **Users:** 유저 공개 정보 및 최근 활동을 통합 반환하는 프로필 조회 구현
        - FastAPI 전역 에러 핸들러(Custom Exceptions)를 통한 예외 처리 구조화
    - **산출물 (Deliverables):** 통합 테스트가 완료된 도메인별 REST API (Swagger UI)

- **Milestone 3: 시스템 통합 및 최종 안정화 (Week 6 ~ Week 7)**
    - **목표:** 백그라운드 아카이브 수집 스케줄러 개발 및 전체 시스템 안정화
    - **주요 작업 (Tasks):**
        - SQLite WAL 모드를 도입하여 동시성 트랜잭션 성능 최적화
        - 1단계 논리 잠금 및 2단계 쓰로틀링 배치 청크 이관을 수행하는 백그라운드 가비지 컬렉터(GC) 개발
        - pytest 기반의 격리 데이터베이스 테스트 환경 구축 및 40개 테스트 케이스 시나리오/단위 테스트 자동화 수행
    - **산출물 (Deliverables):** 백그라운드 작업이 통합된 최종 백엔드 API 서버 및 테스트 보고서

---

## 🛠 Tech Stack

- **Backend Framework:** FastAPI (Python 3.10.20)
- **Database & Data Access:** SQLite3 (WAL 모드 활성화 / Python 내장 `sqlite3` 모듈을 이용한 쿼리(Raw SQL) / ORM 미사용)
- **Authentication & Security:** PyJWT, passlib[bcrypt]
- **Background Scheduler:** APScheduler
- **Testing suite:** pytest, httpx
- **Development Tools:** Git / GitHub, VSCode, Pydantic (Data Validation)