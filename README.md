# 🔥 Modakbul (Bonfire)

**2026-Spring Software Engineering Team Project**

**Instructor:** Jaekwon Lee

---

## 👨‍💻 Team Members & Roles

| Name | Role & Responsibilities | GitHub Profile |
| --- | --- | --- |
| **Kunwoo Kim** | Comment Feature Development, Firewood addition & decay calculation | [Github Profile](https://github.com/goukimesatz) |
| **Yerdos Narzigitov** | Topic Feature Development, Bonfire creation & similarity mapping | [Github Profile](https://github.com/YerdosNar) |
| **Sangjun Jeon** | Setting Feature Development, DB connection & shared configurations | [Github Profile](https://github.com/nclsang) |
| **Kyeongho Cha** | Auth & Garbage Collection Development, Architecture & Scheduler | [Github Profile](https://github.com/Homeria) |

---

## 📖 Project Overview

**Modakbul** is an anonymous community backend API designed for high-density, real-time communication on trending issues.

Every 'Bonfire' (Topic) is granted an initial lifespan of 1 hour upon creation. As users continuously add 'Firewood' (Comments), the lifespan is extended based on a **Variable Burn-Rate and Oxygen Competition Algorithm**. Once interest fades and the lifespan expires, the post is automatically archived and deleted from the active database by a background garbage collector. This ensures data ephemerality, leaving only the most active and fresh discussions available whenever a user connects.

---

## 🎯 Project Vision Statement

- **Target Users:** Anonymous users who want to communicate lightly about real-time issues without the burden of a permanent digital footprint.
- **Problem or Need:** Existing communities preserve posts permanently, leading to information fatigue and unnecessary digital traces.
- **Product Category:** Real-time ephemeral anonymous community API server.
- **Key Benefit & Differentiation:** Assigns a lifespan (`expires_at`) to posts. Utilizes Lazy Deletion and a 2-phase chunked background archiving process to completely remove inactive posts from the active database without a trace.

---

## 📌 Project Goals & Scope

- **Business Goals:** Optimize system resources and manage ephemeral data through a variable burn-rate algorithm and transaction control.
- **In-Scope (Major Features):**
    - JWT token-based user authentication and authorization (Sign-up/Login/Withdrawal).
    - RESTful API implementation for creating Bonfires (Topics) and adding Firewood (Comments).
    - Active feed and expired ("ashes") feed retrieval based on Lazy Deletion using Raw SQL queries.
    - Implementation of the 'Oxygen Competition Variable Burn-Rate' algorithm, where lifespan extensions decay exponentially as comments accumulate and are further reduced if semantically similar topics are highly active.
    - Background scheduler (APScheduler) performing a 2-phase garbage collection (1. Instant logical lock, 2. Throttled chunked archiving migration) to handle database lock concurrency in SQLite.
    - Integrated profile retrieval endpoint returning user summary information along with their recent topics and comments in a single payload.
- **Out-of-Scope:**
    - Complex frontend UI/UX implementation.
    - WebSocket-based real-time data pushes (substituted by optimized REST API for retrieval performance).

---

## 📅 Milestones

- **Milestone 1: Core Architecture & Common Interface Setup (Week 1 ~ Week 2)**
    - **Goal:** Design DB schema and finalize the development contract (Pydantic Schemas) between API and DB tasks.
    - **Tasks:**
        - Design SQLite3-based relational DB schema (users, topics, comments, topic_similarities, ash_topics, ash_comments) and create ERD.
        - Define data I/O forms (Pydantic BaseModel) to establish independent development environments for team members.
        - Initial FastAPI environment setup and skeleton code for routers/dependencies.
        - Configure JWT secret keys and one-way encryption (bcrypt) environment.
    - **Deliverables:** DB schema initialization script (`init_db.py`), API/DTO interface definition document.
        
- **Milestone 2: Domain-specific API & Service/Repository Development (Week 3 ~ Week 5)**
    - **Goal:** Implement actual business logic and endpoints for Auth, Topics, Comments, and Users domains.
    - **Tasks:**
        - **Auth:** Implement sign-up/login/withdrawal and JWT token issuance/validation middleware.
        - **Topics:** Implement Bonfire creation logic, similarity mapping, and active/ashes feed retrieval queries with lazy deletion filtering.
        - **Comments:** Implement Firewood addition with single-transaction control and the oxygen-competition variable burn-rate algorithm.
        - **Users:** Implement integrated profile lookup returning user summary and recent posts/comments.
        - Centralize exception handling via FastAPI Global Error Handlers (Custom Exceptions).
    - **Deliverables:** Domain-specific REST APIs (Swagger UI) with completed integration testing.

- **Milestone 3: System Integration & Final Stabilization (Week 6 ~ Week 7)**
    - **Goal:** Develop background archiving scheduler and stabilize the entire system.
    - **Tasks:**
        - Enable SQLite WAL mode to optimize concurrent transactions.
        - Implement a 2-phase chunked database archiving scheduler (Garbage Collector) to prevent database lock starvation.
        - Build an isolated database testing environment with pytest, automating 40 unit, integration, and scenario test cases.
    - **Deliverables:** Final backend API server integrated with background tasks and automated test suite.
    
---

## 🛠 Tech Stack

- **Backend Framework:** FastAPI (Python 3.10.20)
- **Database & Data Access:** SQLite3 (WAL mode enabled / Raw SQL using Python's built-in `sqlite3` module / No ORM)
- **Authentication & Security:** PyJWT, passlib[bcrypt]
- **Background Scheduler:** APScheduler (2-phase background archiving collector)
- **Testing Suite:** pytest, httpx
- **Development Tools:** Git / GitHub, VSCode, Pydantic (Data Validation)