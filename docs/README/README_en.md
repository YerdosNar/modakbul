# 🔥 Modakbul (모닥불)

**2026 Spring Software Engineering Team Project**

**Instructor:** Jaekwon Lee

---

## 👨‍💻 Team Members & Roles

| Name | Role & Responsibilities | GitHub Profile |
| --- | --- | --- |
| **Kunwoo Kim** | Comment Feature Development | [Github Profile](https://github.com/goukimesatz) |
| **Yerdos Narzigitov** | Topic Feature Development | [Github Profile](https://github.com/YerdosNar) |
| **Sangjun Jeon** | Setting Feature Development | [Github Profile](https://github.com/nclsang) |
| **Kyeongho Cha** | Auth & Garbage Collection Development | [Github Profile](https://github.com/Homeria) |

---

## 📖 Project Overview

**Modakbul** is an anonymous community backend API designed for high-density, real-time communication on trending issues.

Every 'Bonfire' (Topic) is granted an initial lifespan of 1 hour upon creation. As users continuously add 'Firewood' (Comments), the lifespan is extended based on a **Variable Burn-Rate Algorithm**. Once interest fades and the lifespan expires, the post is automatically and permanently deleted from the database. This ensures data ephemerality, leaving only the most active and fresh discussions available whenever a user connects.

---

## 🎯 Project Vision Statement

- **Target Users:** Anonymous users who want to communicate lightly about real-time issues without the burden of a permanent digital footprint.
- **Problem or Need:** Existing communities preserve posts permanently, leading to information fatigue and unnecessary digital traces.
- **Product Category:** Real-time ephemeral anonymous community API server.
- **Key Benefit & Differentiation:** Assigns a lifespan (`expires_at`) to posts. Utilizes Lazy Deletion and background physical deletion to completely remove inactive posts from the database without a trace.

---

## 📌 Project Goals & Scope

- **Business Goals:** Optimize system resources and manage ephemeral data through a variable burn-rate algorithm and transaction control.
- **In-Scope (Major Features):**
    - JWT token-based user authentication and authorization (Sign-up/Login).
    - RESTful API implementation for creating Bonfires (Topics) and adding Firewood (Comments).
    - Active feed retrieval based on Lazy Deletion using Raw SQL queries.
    - Implementation of the 'Variable Burn-Rate' algorithm, where lifespan extension increments diminish as comments accumulate.
    - Background scheduler (APScheduler) to periodically and physically remove expired data.
- **Out-of-Scope:**
    - Complex frontend UI/UX implementation.
    - Archiving systems for permanent preservation of deleted posts.
    - Real-time data pushes via WebSockets (substituted by optimized REST API for retrieval performance).

---

## 👥 Stakeholders & Users

- **Stakeholders:** Development Team (all members), Professor, and TAs.
- **Requirements:** Verification of structural validity regarding how the backend architecture manages concurrency (Race Conditions) and how efficiently it queries and cleans up ephemeral data.
- **Users:** Individuals who wish to enjoy discussions on hot topics without leaving a personal trace.

---

## 📅 Milestones

- **Milestone 1: Core Architecture & Common Interface Setup (Week 1 ~ Week 2)**
    - **Goal:** Design DB schema and finalize the development contract (Pydantic Schemas) between API and DB tasks.
    - **Tasks:**
        - Design SQLite3-based relational DB schema (users, topics, comments) and create ERD.
        - Define data I/O forms (Pydantic BaseModel) to establish independent development environments for team members.
        - Initial FastAPI environment setup and skeleton code for routers/CRUD.
        - Configure JWT secret keys and one-way encryption (bcrypt) environment.
    - **Deliverables:** DB schema initialization script (`init_db.py`), API/CRUD interface definition document.
        
- **Milestone 2: Domain-specific API & CRUD Sequential Development (Week 3 ~ Week 5)**
    - **Goal:** Implement actual business logic and endpoints for Auth, Topics, and Comments domains.
    - **Tasks:**
        - **Auth:** Implement sign-up/login and JWT token issuance/validation middleware.
        - **Topics:** Implement Bonfire creation logic and feed retrieval queries with lazy deletion filtering (`WHERE expires_at > now()`).
        - **Comments:** Implement Firewood addition with single-transaction control and the 'Variable Burn-Rate' lifespan extension algorithm.
        - Centralize exception handling via FastAPI Global Error Handlers (Custom Exceptions).
    - **Deliverables:** Domain-specific REST APIs (Swagger UI) with completed integration testing.

- **Milestone 3: System Integration & Final Stabilization (Week 6 ~ Week 7)**
    - **Goal:** Develop centralized configuration and Garbage Collector scheduler; stabilize the entire system.
    - **Tasks:**
        - Implement physical hard delete (`DELETE`) for expired data using asynchronous background tasks (APScheduler).
        - Conduct integration tests for all API endpoints and inspect concurrency issues.
        - Patch features prone to potential bugs.
    - **Deliverables:** Final backend API server integrated with background tasks and the final team project report.
    
---

## 🛠 Tech Stack

- **Backend Framework:** FastAPI (Python 3.10.20)
- **Database & Data Access:** SQLite3 (Raw SQL using Python's built-in `sqlite3` module / No ORM)
- **Authentication & Security:** PyJWT, passlib[bcrypt]
- **Background Scheduler:** APScheduler
- **Deployment & Infra:** TBD
- **Development Tools:** Git / GitHub, VSCode, Pydantic (Data Validation)