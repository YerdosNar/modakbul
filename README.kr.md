# 모닥불 (Modakbul)

**2026-Spring Software Engineering Team Project**

**Instructor:** Jaekwon Lee

---

[**English**](./README.md) | [한국어]

## 👨‍💻 Team Members & Roles

| Name | Role & Responsibilities | GitHub Profile |
| --- | --- | --- |
| **김건우** | Role 1 / ~ | [Github Profile](https://github.com/goukimesatz) |
| **나르지기토브 예르도스** | Role 2 / ~ | [Github Profile](https://github.com/YerdosNar) |
| **전상준** | Role 3 / ~ | [Github Profile](https://github.com/nclsang) |
| **차경호** | Role 4 / ~ | [Github Profile](https://github.com/Homeria) |

---

## 📖 Project Overview

**모닥불 (Modakbul)**는 현재 화제가 되는 이슈에 대해 실시간으로 밀도 있게 소통할 수 있는 익명 커뮤니티 백엔드 API 입니다. 사용자들이 지속적으로 '장작(댓글)'을 추가하지 않으면 게시물의 '화력(HP)'이 줄어들고 결국 파괴(삭제)되는 시스템을 통해, 언제 접속하든 지금 가장 활발하게 논의되는 신선한 주제만 남게 됩니다.

---

## 🎯 Project Vision Statement

- **Target Users:** 영구적인 디지털 발자국이 남는 것을 부담스러워하며 실시간 이슈에 대해 소통하고 싶은 익명 사용자
- **Problem or Need:** 기존 커뮤니티는 한 번 작성된 글이 영구 보존되어 정보의 피로감과 불필요한 흔적을 남김.
- **Product Category:** 실시간 휘발성 익명 커뮤니티 API 서버.
- **Key Benefit & Differentiation:** 게시물에 '화력(HP)'이라는 수명을 부여하여, 사용자의 참여(장작)가 없는 게시물은 데이터베이스에서 영구적으로 자동 소멸됨.

---

## 📌 Project Goals & Scope

- **Business Goals:** 실시간 HP 감소 및 게시물 소멸 로직 처리 시스템 구축.
- **In-Scope (Major Features):**
    - 모닥불(게시물) 생성 및 장작(댓글 등) 추가를 위한 RESTful API 구현
    - ▲ WebSocket을 활용한 실시간 화력(HP) 상태 브로드캐스팅 및 클라이언트 동기
    - 일정 주기로 화력(HP)을 감소시키고 0이 될 경우 데이터를 삭제하는 백그라운드 스케줄러(Background Scheduler)
	- 세션/IP 기반 익명 사용자 기준
- **Out-of-Scope:**
    - 복잡한 프론트엔드 UI/UX 구현
    - 삭제된 게시물의 영구 보존용 아카이빙 시스템
    - 회원가입 및 인증 절차

---

## 👥 Stakeholders & Users

- **Stakeholders:** 개발 팀(팀원 전체), 교수님 및 조교님.
- **Requirements:** 백엔드 아키텍처가 실시간 데이터 처리와 백그라운드 작업을 얼마나 효율적으로 처리하는지 구조작 타당성 검증.
- **Users:** 휘발성 이슈 토론을 즐기는 익명의 사용자.

---

## 📅 Milestones

- **-** .


기준 : 선 커뮤니티 후 모닥불 로직 적용

1. 커뮤니티 시스템 구축
	기능
		1. GET(조회) - 게시물 목록 가져오기,
		2. POST(생성) - 카테고리(키워드) 생성, 게시물 생성?
		3. PUT(수정) - 게시물 수정?
		4. DELETE(삭제) - 게시물 선택 삭제
	기술
		1. DB
		2. Reverse Proxy
		3. API 엔드포인트 제작?

2. 모닥불 로직 적용
	기능
		1. GET(조회) - 모닥불 HP 조회
		2. POST(생성) - 1-2 카테고리 생성에 HP도 등록하도록 파라미터 추가
		3. PUT(수정) - ?
		4. DELETE(삭제) - ?
	기술
		1. 스레드(백그라운드로 로직 처리)
		2.

3. 최적화
	기능
		1. 주기적으로 조회해야 하는 데이터는 WebSocket으로 변환
		2.

---

## 🛠 Tech Stack

- **Backend Framework:** ~
- **Database & ORM:** ~
- **Real-time Communication:** ~
- **Deployment & Tools:** ~
