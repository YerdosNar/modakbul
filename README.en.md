# Modakbul (모닥불)

**2026-Spring Software Engineering Team Project**

**Instructor:** Jaekwon Lee

---

[English] | [**한국어**](/README.kr.md)

---

## 👨‍💻 Team Members & Roles

| Name | Role & Responsibilities | GitHub Profile |
| --- | --- | --- |
| **Gunwoo Kim** | Role 1 / ~ | [**goukimesatz**](https://github.com/goukimesatz) |
| **Yerdos Narzigitov** | Role 2 / ~ | [**YerdosNar**](https://github.com/YerdosNar) |
| **Sangjun Jeon** | Role 3 / ~ | [**nclsang**](https://github.com/nclsang) |
| **Kyungho Cha** | Role 4 / ~ | [**Homeria**](https://github.com/Homeria) |

---

## 📖 Project Overview

**Modakbul** is an anonymous community backend API where users can communicate intensely about trending issues in real-time. If users stop adding "Firewood" (comments), the post's "Firepower" (HP) decreases until it is eventually "Extinguished" (deleted). This system ensures that only the freshest and most active topics remain visible.

---

## 🎯 Project Vision Statement

- **Target Users:** Anonymous users who want to discuss real-time issues without the burden of a permanent digital footprint.
- **Problem or Need:** Existing communities archive posts permanently, leading to information fatigue and unnecessary digital traces.
- **Product Category:** Real-time volatile anonymous community API server.
- **Key Benefit & Differentiation:** By assigning a lifespan (HP) to posts, content that lacks user engagement (firewood) is automatically and permanently removed from the database.

---

## 📌 Project Goals & Scope

- **Business Goals:** Build a system to handle real-time HP reduction and post-deletion logic.
- **In-Scope (Major Features):**
    - Implement RESTful APIs for creating "Bonfires" (posts) and adding "Firewood" (comments).
    - Use WebSockets for real-time broadcasting of Firepower (HP) status and client synchronization.
    - Background Scheduler to decrease HP at regular intervals and delete data when it reaches zero.
    - Anonymous user identification based on Session/IP.
- **Out-of-Scope:**
    - Complex frontend UI/UX implementation.
    - Archiving systems for deleted posts.
    - User registration and authentication procedures.

---

## 👥 Stakeholders & Users

- **Stakeholders:** Development team, Professor, and TAs.
- **Requirements:** Structural validation of how efficiently the backend architecture handles real-time data processing and background tasks.
- **Users:** Anonymous users who enjoy discussing volatile, trending issues.

---

## 📅 Milestones
*Criteria: Build community system first, then apply Modakbul logic.*

1. **Community System Construction**
    - **Features:**
        - GET (List posts),
        - POST (Create category/post),
        - PUT (Update post),
        - DELETE (Manual deletion).
    - **Tech:** DB, Reverse Proxy, API Endpoints.

2. **Applying Modakbul Logic**
    - **Features:**
        - GET (Check HP),
        - POST (Register HP parameters during creation).
    - **Tech:** Multi-threading (Background logic processing).

3. **Optimization**
    - **Features:** Convert frequently polled data to WebSockets.

---

## 🛠 Tech Stack

- **Backend Framework:** Spring Boot (Java 21)
- **Database & ORM:** PostgreSQL / JPA
- **Real-time Communication:** WebSockets
- **Deployment & Tools:** Docker, Caddy (Reverse Proxy)
